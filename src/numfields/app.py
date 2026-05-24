"""GLFW + moderngl + ImGui application loop."""

from __future__ import annotations

import sys

import glfw
import moderngl
from imgui_bundle import imgui
from imgui_bundle.python_backends.glfw_backend import GlfwRenderer

import numfields.domain.bodies  # noqa: F401 — register body types
from numfields.domain.scene import Scene
from numfields.rendering.camera import OrbitCamera
from numfields.rendering.renderer import SceneRenderer
from numfields.rendering.shader_program import load_shader_pair
from numfields.rendering.viewport_fbo import ViewportFBO
from numfields.ui.panels import AddMenuPanel, HierarchyPanel, InspectorPanel, ViewportPanel
from numfields.ui.theme import apply_theme

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800
TITLE = "numfields — Electrostatics Scene Builder"


class Application:
    def __init__(self) -> None:
        if not glfw.init():
            raise RuntimeError("Failed to initialize GLFW")

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)

        self.window = glfw.create_window(
            WINDOW_WIDTH, WINDOW_HEIGHT, TITLE, None, None
        )
        if not self.window:
            glfw.terminate()
            raise RuntimeError("Failed to create GLFW window")

        glfw.make_context_current(self.window)
        glfw.swap_interval(1)

        self.ctx = moderngl.create_context()
        imgui.create_context()
        self._imgui_impl = GlfwRenderer(self.window)
        apply_theme()
        io = imgui.get_io()
        io.config_flags |= imgui.ConfigFlags_.docking_enable

        vert_s, frag_s = load_shader_pair("solid.glsl")
        self._solid_program = self.ctx.program(vertex_shader=vert_s, fragment_shader=frag_s)
        vert_l, frag_l = load_shader_pair("line.glsl")
        self._line_program = self.ctx.program(vertex_shader=vert_l, fragment_shader=frag_l)

        self.scene = Scene()
        self.camera = OrbitCamera()
        self.renderer = SceneRenderer(self.ctx, self._solid_program, self._line_program)
        self.fbo = ViewportFBO(self.ctx)

        self.viewport_panel = ViewportPanel()
        self.hierarchy_panel = HierarchyPanel()
        self.add_panel = AddMenuPanel()
        self.inspector_panel = InspectorPanel()

        self._last_mouse = (0.0, 0.0)
        self._lmb_down = False
        self._mmb_down = False
        self._first_dock = True
        self._keys_prev: dict[int, bool] = {}

    def _setup_docking(self) -> None:
        viewport = imgui.get_main_viewport()
        dockspace_id = imgui.get_id("NumFieldsDockSpace")
        
        if self._first_dock:
            self._first_dock = False
            from imgui_bundle.imgui import internal as imgui_internal
            
            imgui_internal.dock_builder_remove_node(dockspace_id)
            imgui_internal.dock_builder_add_node(dockspace_id, imgui.DockNodeFlags_.passthru_central_node)
            imgui_internal.dock_builder_set_node_size(dockspace_id, viewport.size)
            
            ratio = 250.0 / max(viewport.size.x, 1.0)
            _, dock_left, dock_main = imgui_internal.dock_builder_split_node_py(
                dockspace_id, imgui.Dir_.left, ratio
            )
            
            # Split the sidebar vertically
            _, dock_left_top, dock_left_bottom = imgui_internal.dock_builder_split_node_py(
                dock_left, imgui.Dir_.up, 0.33
            )
            _, dock_left_mid, dock_left_bot = imgui_internal.dock_builder_split_node_py(
                dock_left_bottom, imgui.Dir_.up, 0.5
            )
            
            imgui_internal.dock_builder_dock_window("Viewport", dock_main)
            imgui_internal.dock_builder_dock_window("Hierarchy", dock_left_top)
            imgui_internal.dock_builder_dock_window("Add Body", dock_left_mid)
            imgui_internal.dock_builder_dock_window("Inspector", dock_left_bot)
            
            imgui_internal.dock_builder_finish(dockspace_id)

        imgui.dock_space_over_viewport(
            dockspace_id,
            viewport,
            imgui.DockNodeFlags_.passthru_central_node,
        )

    def _handle_camera_input(self) -> None:
        vp = self.viewport_panel.input
        io = imgui.get_io()
        
        from imgui_bundle.imguizmo import im_guizmo
        alt_orbit = io.key_alt
        gizmo_using = im_guizmo.is_using() and not alt_orbit

        if not vp.allow_camera() or gizmo_using:
            self._lmb_down = glfw.get_mouse_button(self.window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS
            self._mmb_down = glfw.get_mouse_button(self.window, glfw.MOUSE_BUTTON_MIDDLE) == glfw.PRESS
            return

        if io.want_capture_mouse and not alt_orbit:
            self._lmb_down = False
            self._mmb_down = False
            return

        mx, my = io.mouse_pos.x, io.mouse_pos.y
        dx = mx - self._last_mouse[0]
        dy = my - self._last_mouse[1]
        self._last_mouse = (mx, my)

        lmb = glfw.get_mouse_button(self.window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS
        mmb = glfw.get_mouse_button(self.window, glfw.MOUSE_BUTTON_MIDDLE) == glfw.PRESS

        # Picking
        if lmb and not self._lmb_down:
            if 0 <= vp.mouse_x < self.fbo.width and 0 <= vp.mouse_y < self.fbo.height:
                body_idx = self.fbo.read_picking(int(vp.mouse_x), int(vp.mouse_y))
                if body_idx > 0:
                    bodies = self.scene.bodies()
                    if body_idx <= len(bodies):
                        self.scene.select(bodies[body_idx - 1].id)
                else:
                    self.scene.select(None)

        if lmb and self._lmb_down:
            self.camera.orbit(dx, dy)
        if mmb and self._mmb_down:
            self.camera.pan(dx, dy)

        self._lmb_down = lmb
        self._mmb_down = mmb

        if io.mouse_wheel != 0:
            self.camera.zoom(io.mouse_wheel)

    def _render_viewport(self) -> None:
        w, h = self.viewport_panel.size
        self.fbo.resize(int(w), int(h))
        self.camera.aspect = w / h if h > 0 else 1.0

        self.fbo.bind()
        self.fbo.clear()
        sel = self.scene.selected_id()
        sel_str = str(sel) if sel else None
        self.renderer.render(
            self.scene,
            self.camera,
            sel_str,
            translating=self.viewport_panel.gizmo_translating,
        )
        self.ctx.screen.use()

    def _draw_ui(self) -> None:
        self._setup_docking()
        self.viewport_panel.draw(self.fbo.texture_id, self.renderer, self.scene, self.camera)
        self.hierarchy_panel.draw(self.scene)
        self.add_panel.draw(self.scene)
        self.inspector_panel.draw(self.scene)
        self._handle_delete_selected()

    def _shift_down(self) -> bool:
        return (
            glfw.get_key(self.window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS
            or glfw.get_key(self.window, glfw.KEY_RIGHT_SHIFT) == glfw.PRESS
        )

    def _ctrl_down(self) -> bool:
        return (
            glfw.get_key(self.window, glfw.KEY_LEFT_CONTROL) == glfw.PRESS
            or glfw.get_key(self.window, glfw.KEY_RIGHT_CONTROL) == glfw.PRESS
        )

    def _key_just_pressed(self, key: int) -> bool:
        down = glfw.get_key(self.window, key) == glfw.PRESS
        prev = self._keys_prev.get(key, False)
        self._keys_prev[key] = down
        return down and not prev

    def _just_pressed_key_labels(self, *keys: int) -> list[str]:
        labels: list[str] = []
        for key in keys:
            if not self._key_just_pressed(key):
                continue
            labels.append((glfw.get_key_name(key, 0) or "").lower())
        return labels

    def _handle_undo_redo(self) -> None:
        io = imgui.get_io()
        if io.want_text_input and imgui.is_any_item_active():
            return

        if not self._ctrl_down():
            self._key_just_pressed(glfw.KEY_Z)
            self._key_just_pressed(glfw.KEY_Y)
            return

        shift = self._shift_down()
        for label in self._just_pressed_key_labels(glfw.KEY_Z, glfw.KEY_Y):
            if label == "z" and not shift:
                self.scene.undo()
                return
            if label == "y" and not shift:
                self.scene.redo()
                return
            if label == "z" and shift:
                self.scene.redo()
                return

    def _handle_delete_selected(self) -> None:
        selected_id = self.scene.selected_id()
        if selected_id is None:
            return
        io = imgui.get_io()
        if io.want_text_input:
            return
        if imgui.is_key_pressed(imgui.Key.delete):
            self.scene.remove(selected_id)

    def run(self) -> None:
        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            self._imgui_impl.process_inputs()
            self.ctx.screen.clear(0.15, 0.15, 0.15, 1.0)
            imgui.new_frame()

            from imgui_bundle.imguizmo import im_guizmo
            im_guizmo.begin_frame()

            self._handle_undo_redo()
            self._draw_ui()
            self._handle_camera_input()
            self._render_viewport()

            imgui.render()
            self._imgui_impl.render(imgui.get_draw_data())
            glfw.swap_buffers(self.window)

        self.shutdown()

    def shutdown(self) -> None:
        self.renderer.release()
        self.fbo.release()
        self._imgui_impl.shutdown()
        glfw.terminate()


def run_app() -> None:
    try:
        Application().run()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise
