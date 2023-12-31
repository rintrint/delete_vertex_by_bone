bl_info = {
    "name": "delete_vertex_by_bone", 
    "description": "no description",
    "author": "rint",
    "version": (0, 0, 2),
    "blender": (3, 0, 0),
    "location": "View3D",
    "category": "Object",
}

import bpy

class delete_vertex_by_bone_panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "rint"
    bl_label = "Reduce Faces Tool"
    
    def draw(self, context):
        layout = self.layout
        col = self.layout.column(align=True)
        #col.label(text='Reduce Faces Tool:', icon='BLENDER')
        
        grid = col.grid_flow(row_major=True, align=True)
        
        row = grid.row(align=True)
        row.operator_context = 'EXEC_DEFAULT'
        op = row.operator('delete_vertex_by_bone.delete_vertex', text='Delete vertex by bone', icon='ERROR')

class Delete_Vertex(bpy.types.Operator):
    bl_idname = 'delete_vertex_by_bone.delete_vertex'
    bl_label = 'delete_vertex'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context: bpy.types.Context):
        # 開始計時
        import time
        start_time = time.time()
        
        import bmesh
        def delete_vertices_based_on_selected_bones_weights():
            armature = bpy.context.active_object
            if armature and armature.type == 'ARMATURE':
                
                #當前物體是骨架時進入姿態模式
                bpy.ops.object.mode_set(mode='POSE')
                
                selected_pose_bone = bpy.context.selected_pose_bones
                selected_pose_bone_name = [bone.name for bone in selected_pose_bone]
                
                #進入物體模式
                bpy.ops.object.mode_set(mode='OBJECT')
                
                # 获取骨架的所有子网格体
                child_meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH' and obj.parent == armature]

                # 选择所有子网格体
                bpy.ops.object.select_all(action='DESELECT')
                for child_mesh in child_meshes:
                    child_mesh.select_set(True)

                # 将活动对象设置为第一个子网格体
                bpy.context.view_layer.objects.active = child_meshes[0]
                
                # 清理頂點組 避免刪除權重為0的頂點
                bpy.ops.object.vertex_group_clean(group_select_mode='BONE_DEFORM', limit=0.0, keep_single=False)
                
                selected_bones = selected_pose_bone_name
                for mesh_obj in bpy.context.selected_objects:
                    if mesh_obj.type == "MESH": # 如果對象是網格體
                        # 創建一個bmesh對象來操作網格體的頂點
                        bm = bmesh.new()
                        bm.from_mesh(mesh_obj.data)
                        
                        # 版本1(33秒)
                        ## 遍歷每個網格體的每個頂點，檢查它是否受到選擇的骨骼的影響，如果是，就將它刪除
                        #verts_to_remove = []
                        #for v in bm.verts:
                        #    # 獲取頂點的權重字典，鍵是骨骼的名字，值是權重值
                        #    # 先獲取頂點在mesh中的索引
                        #    index = v.index
                        #    # 再用mesh_obj.data.vertices[index].groups來訪問groups屬性
                        #    weights = {g.name: g.weight for g in mesh_obj.vertex_groups if g.index in [vg.group for vg in mesh_obj.data.vertices[index].groups]}
                        #    # 如果頂點受到選擇的骨骼的影響，就將它刪除
                        #    if any(bone in weights for bone in selected_bones):
                        #        #bm.verts.remove(v)
                        #        verts_to_remove.append(v)
                        #bmesh.ops.delete(bm, geom=verts_to_remove, context='VERTS')
                        
                        # 版本2(18秒)
                        #selected_bones = set(selected_bones)
                        #verts_to_remove = [v for v in bm.verts if selected_bones.intersection(g.name for g in mesh_obj.vertex_groups if v.index in [vg.group for vg in mesh_obj.data.vertices[v.index].groups])]
                        #bmesh.ops.delete(bm, geom=verts_to_remove, context='VERTS')
                        
                        # 版本3(0.15秒)
                        selected_bones = set(selected_bones)
                        vertex_groups = list(mesh_obj.vertex_groups) # リストに変換
                        verts_to_remove = [v for v in bm.verts if selected_bones.intersection(vertex_groups[i].name for i in (vg.group for vg in mesh_obj.data.vertices[v.index].groups))] # ジェネレータ式を使う
                        bm.verts.ensure_lookup_table() # ルックアップテーブルを作成
                        bmesh.ops.delete(bm, geom=verts_to_remove, context='VERTS')
                        
                        # 更新每個網格體的數據並釋放bmesh對象
                        bm.to_mesh(mesh_obj.data)
                        bm.free()
            
            #再次進入姿態模式
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='POSE')
        delete_vertices_based_on_selected_bones_weights()
        
        # 結束計時
        end_time = time.time()
        execution_time = end_time - start_time
        execution_time = round(execution_time, 2)
        self.report({'INFO'}, f"Finished in {execution_time}s.")
        
        return {'FINISHED'}

classes = (
	delete_vertex_by_bone_panel,
    Delete_Vertex
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    # 翻譯
    from delete_vertex_by_bone.m17n import translation_dict
    bpy.app.translations.register(bl_info['name'], translation_dict)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    # 翻譯
    bpy.app.translations.unregister(bl_info['name'])

# 插件名可以改一下，容易辨識，也可以不改，不會導致衝突
# bl_idname不能和其他插件一樣，插件同時啟用會導致衝突
# classes名不能和其他插件一樣，插件同時啟用會導致衝突
# Test_Panel3.bl_category和其他插件一樣就會放在一起
