"""3D viewport panel — FBO display and focus tracking."""

from __future__ import annotations

from imgui_bundle import imgui

from numfields.domain.scene import Scene
from numfields.rendering.camera import OrbitCamera
from numfields.rendering.renderer import SceneRenderer
from numfields.ui.input import ViewportInput


class ViewportPanel:
    def __init__(self) -> None:
        self.input = ViewportInput()
        self.size = (640.0, 480.0)

    def draw(self, texture_id: int, renderer: SceneRenderer, scene: Scene, camera: OrbitCamera) -> None:
        imgui.push_style_var(imgui.StyleVar_.window_padding, imgui.ImVec2(0, 0))
        expanded, _ = imgui.begin("Viewport", flags=imgui.WindowFlags_.no_scrollbar)
        if expanded:
            avail = imgui.get_content_region_avail()
            w = max(64.0, avail.x)
            h = max(64.0, avail.y)
            self.size = (w, h)
            self.input.hovered = imgui.is_window_hovered()
            self.input.focused = imgui.is_window_focused()
            pos = imgui.get_cursor_screen_pos()
            self.input.mouse_x = imgui.get_io().mouse_pos.x - pos.x
            self.input.mouse_y = imgui.get_io().mouse_pos.y - pos.y
            if texture_id:
                imgui.image(
                    imgui.ImTextureRef(texture_id),
                    imgui.ImVec2(w, h),
                    uv0=imgui.ImVec2(0, 1),
                    uv1=imgui.ImVec2(1, 0),
                )
                
                # Overlay toggles
                imgui.set_cursor_pos(imgui.ImVec2(15, 35))
                imgui.push_style_color(imgui.Col_.text, imgui.ImVec4(0.8, 0.8, 0.8, 1.0))
                _, renderer.show_grid = imgui.checkbox("Grid", renderer.show_grid)
                imgui.set_cursor_pos(imgui.ImVec2(15, 65))
                _, renderer.show_axes = imgui.checkbox("Axes", renderer.show_axes)
                imgui.pop_style_color()

                # Overlay ImGuizmo
                selected = scene.selected()
                if selected is not None:
                    from imgui_bundle import imguizmo
                    import numpy as np
                    import glm
                    
                    imguizmo.im_guizmo.set_orthographic(False)
                    imguizmo.im_guizmo.set_drawlist()
                    imguizmo.im_guizmo.set_rect(pos.x, pos.y, w, h)
                    
                    view = camera.view_matrix()
                    proj = camera.projection_matrix()
                    model = selected.transform.matrix()
                    
                    view_list = list(np.array(glm.transpose(view), dtype=float).flatten())
                    proj_list = list(np.array(glm.transpose(proj), dtype=float).flatten())
                    model_list = list(np.array(glm.transpose(model), dtype=float).flatten())
                    
                    view_mat16 = imguizmo.im_guizmo.Matrix16(view_list)
                    proj_mat16 = imguizmo.im_guizmo.Matrix16(proj_list)
                    model_mat16 = imguizmo.im_guizmo.Matrix16(model_list)
                    
                    modified = imguizmo.im_guizmo.manipulate(
                        view_mat16,
                        proj_mat16,
                        imguizmo.im_guizmo.OPERATION.translate,
                        imguizmo.im_guizmo.MODE.local,
                        model_mat16
                    )
                    
                    if modified:
                        comps = imguizmo.im_guizmo.decompose_matrix_to_components(model_mat16)
                        selected.transform.position = glm.vec3(*comps.translation.values)
                        selected.transform.set_euler_degrees(*comps.rotation.values)
                        # Gizmo scale can be non-uniform, but we only have uniform scale in MVP
                        selected.transform.scale = comps.scale.values[0]
                        scene.mark_dirty()
                        
                    is_using = imguizmo.im_guizmo.is_using()
                    was_using = getattr(self, '_was_using_gizmo', False)
                    if was_using and not is_using:
                        p = selected.transform.position
                        selected.transform.position = glm.vec3(round(p.x), round(p.y), round(p.z))
                        scene.mark_dirty()
                    self._was_using_gizmo = is_using
                
            else:
                imgui.dummy(imgui.ImVec2(w, h))
        imgui.end()
        imgui.pop_style_var()
