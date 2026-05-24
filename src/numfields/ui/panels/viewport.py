"""3D viewport panel — FBO display and focus tracking."""

from __future__ import annotations

from imgui_bundle import imgui

from numfields.domain.scene import Scene
from numfields.rendering.camera import OrbitCamera
from numfields.rendering.renderer import SceneRenderer
from numfields.ui.gizmo_utils import glm_to_matrix16, sync_transform_from_gizmo
from numfields.ui.input import ViewportInput


class ViewportPanel:
    def __init__(self) -> None:
        self.input = ViewportInput()
        self.size = (640.0, 480.0)
        self.gizmo_translating = False
        self.gizmo_using = False

    def draw(self, texture_id: int, renderer: SceneRenderer, scene: Scene, camera: OrbitCamera) -> None:
        imgui.push_style_var(imgui.StyleVar_.window_padding, imgui.ImVec2(0, 0))
        expanded, _ = imgui.begin("Viewport", flags=imgui.WindowFlags_.no_scrollbar)
        if expanded:
            self.gizmo_translating = False
            self.gizmo_using = False
            avail = imgui.get_content_region_avail()
            w = max(64.0, avail.x)
            h = max(64.0, avail.y)
            self.size = (w, h)
            pos = imgui.get_cursor_screen_pos()
            io = imgui.get_io()
            self.input.mouse_x = io.mouse_pos.x - pos.x
            self.input.mouse_y = io.mouse_pos.y - pos.y

            # Reserve viewport space without capturing mouse (imgui.image blocks ImGuizmo).
            imgui.dummy(imgui.ImVec2(w, h))
            self.input.hovered = imgui.is_item_hovered()
            self.input.focused = imgui.is_window_focused() and self.input.hovered

            if texture_id:
                imgui.get_window_draw_list().add_image(
                    imgui.ImTextureRef(texture_id),
                    imgui.ImVec2(pos.x, pos.y),
                    imgui.ImVec2(pos.x + w, pos.y + h),
                    uv_min=imgui.ImVec2(0, 1),
                    uv_max=imgui.ImVec2(1, 0),
                )

                # Overlay toggles
                imgui.set_cursor_pos(imgui.ImVec2(15, 35))
                imgui.push_style_color(imgui.Col_.text, imgui.ImVec4(0.8, 0.8, 0.8, 1.0))
                _, renderer.show_grid = imgui.checkbox("Grid", renderer.show_grid)
                imgui.set_cursor_pos(imgui.ImVec2(15, 65))
                _, renderer.show_axes = imgui.checkbox("Axes", renderer.show_axes)
                imgui.pop_style_color()

                # Overlay ImGuizmo (after UI widgets; uses screen-space hit testing).
                selected = scene.selected()
                alt_held = io.key_alt
                if selected is not None and not alt_held:
                    from imgui_bundle import imguizmo
                    import glm

                    imguizmo.im_guizmo.set_orthographic(False)
                    imguizmo.im_guizmo.set_drawlist()
                    imguizmo.im_guizmo.set_rect(pos.x, pos.y, w, h)

                    if imgui.is_mouse_clicked(imgui.MouseButton_.left) and imguizmo.im_guizmo.is_over(
                        imguizmo.im_guizmo.OPERATION.translate
                    ):
                        scene.history.start_group(scene)

                    view_mat16 = glm_to_matrix16(camera.view_matrix())
                    proj_mat16 = glm_to_matrix16(camera.projection_matrix())
                    model_mat16 = glm_to_matrix16(selected.transform.matrix())

                    modified = imguizmo.im_guizmo.manipulate(
                        view_mat16,
                        proj_mat16,
                        imguizmo.im_guizmo.OPERATION.translate,
                        imguizmo.im_guizmo.MODE.local,
                        model_mat16,
                    )

                    if modified:
                        sync_transform_from_gizmo(selected.transform, model_mat16)
                        scene.mark_dirty()

                    is_using = imguizmo.im_guizmo.is_using()
                    was_using = getattr(self, "_was_using_gizmo", False)
                    if was_using and not is_using:
                        p = selected.transform.position
                        selected.transform.position = glm.vec3(round(p.x), round(p.y), round(p.z))
                        scene.mark_dirty()
                        scene.history.end_group(scene)
                    self._was_using_gizmo = is_using
                    self.gizmo_translating = is_using
                    self.gizmo_using = is_using
                elif selected is not None:
                    self._was_using_gizmo = False
                
            else:
                imgui.dummy(imgui.ImVec2(w, h))
        imgui.end()
        imgui.pop_style_var()
