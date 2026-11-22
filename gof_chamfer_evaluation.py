import numpy as np
import trimesh
import open3d as o3d
from scipy.spatial import KDTree

def evaluate_chamfer_distance(gof_mesh_path, gt_mesh_path, num_samples=50000):
    print("-> Lade Meshes...")
    mesh_gof = trimesh.load(gof_mesh_path)
    mesh_gt = trimesh.load(gt_mesh_path)
    
    print(f"-> Taste jeweils {num_samples} Punkte von den Oberflächen ab...")
    pts_gof = mesh_gof.sample(num_samples)
    pts_gt = mesh_gt.sample(num_samples)
    
    # In Open3D Punktewolken konvertieren
    pcd_gof = o3d.geometry.PointCloud()
    pcd_gof.points = o3d.utility.Vector3dVector(pts_gof)
    
    pcd_gt = o3d.geometry.PointCloud()
    pcd_gt.points = o3d.utility.Vector3dVector(pts_gt)
    
    print("-> Starte globales Alignment (Skalierung, Rotation & Translation)...")
    # Umkorrigieren: Schwerpunkte matchen
    center_gof = pcd_gof.get_center()
    center_gt = pcd_gt.get_center()
    
    pcd_gof.translate(-center_gof)
    pcd_gt.translate(-center_gt)
    
    # Maßstab (Scale) über die Ausdehnung der Bounding Boxen schätzen
    bbox_gof = pcd_gof.get_axis_aligned_bounding_box()
    bbox_gt = pcd_gt.get_axis_aligned_bounding_box()
    
    scale_factor = np.mean(bbox_gt.get_extent() / bbox_gof.get_extent())
    print(f"-> Berechneter Skalierungsfaktor: {scale_factor:.4f}")
    pcd_gof.scale(scale_factor, center=(0, 0, 0))
    
    # Normalen berechnen für ICP
    pcd_gof.estimate_normals()
    pcd_gt.estimate_normals()
    
    # Grobe Ausrichtung (Globale Registrierung via RANSAC / FPFH Features)
    voxel_size = np.max(bbox_gt.get_extent()) * 0.05
    
    def preprocess_point_cloud(pcd, voxel_size):
        pcd_down = pcd.voxel_down_sample(voxel_size)
        pcd_down.estimate_normals(
            o3d.geometry.KDTreeSearchParamHybrid(radius=voxel_size * 2, max_nn=30))
        pcd_fpfh = o3d.pipelines.registration.compute_fpfh_feature(
            pcd_down,
            o3d.geometry.KDTreeSearchParamHybrid(radius=voxel_size * 5, max_nn=100))
        return pcd_down, pcd_fpfh

    pcd_gof_down, fpfh_gof = preprocess_point_cloud(pcd_gof, voxel_size)
    pcd_gt_down, fpfh_gt = preprocess_point_cloud(pcd_gt, voxel_size)
    
    distance_threshold = voxel_size * 1.5
    result_ransac = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(
        pcd_gof_down, pcd_gt_down, fpfh_gof, fpfh_gt, True, distance_threshold,
        o3d.pipelines.registration.TransformationEstimationPointToPoint(False), 3,
        [o3d.pipelines.registration.CorrespondenceCheckerBasedOnEdgeLength(0.9),
         o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(distance_threshold)],
        o3d.pipelines.registration.RANSACConvergenceCriteria(100000, 0.999))
    
    pcd_gof.transform(result_ransac.transformation)
    
    # Feinausrichtung mit Point-to-Plane ICP
    print("-> Verfeinere Ausrichtung mittels Point-to-Plane ICP...")
    icp_threshold = voxel_size * 0.2
    result_icp = o3d.pipelines.registration.registration_icp(
        pcd_gof, pcd_gt, icp_threshold, np.eye(4),
        o3d.pipelines.registration.TransformationEstimationPointToPlane())
    
    pcd_gof.transform(result_icp.transformation)
    print("-> Alignment erfolgreich abgeschlossen.")
    
    # Zurück zu NumPy Arrays für Chamfer Distance
    final_pts_gof = np.asarray(pcd_gof.points)
    final_pts_gt = np.asarray(pcd_gt.points)
    
    print("-> Berechne Chamfer Distance...")
    tree_gof = KDTree(final_pts_gof)
    tree_gt = KDTree(final_pts_gt)
    
    dist_gof_to_gt, _ = tree_gt.query(final_pts_gof)
    dist_gt_to_gof, _ = tree_gof.query(final_pts_gt)
    
    # CD L1 (Durchschnittlicher absoluter Abstand in den Einheiten des CAD-Modells)
    cd_l1 = 0.5 * (np.mean(dist_gof_to_gt) + np.mean(dist_gt_to_gof))
    # CD L2 (Quadrierter Fehler)
    cd_l2 = np.mean(dist_gof_to_gt**2) + np.mean(dist_gt_to_gof**2)
    
    print("
=== EVALUIERUNGSERGEBNISSE ===")
    print(f"Chamfer Distance (L1 / Mittlerer Abstand): {cd_l1:.6f}")
    print(f"Chamfer Distance (L2 / Quadrierter Fehler): {cd_l2:.6f}")
    
    # Optional: Einheiten-Erkennung basierend auf CAD-Ausdehnung
    extent = bbox_gt.get_extent()
    if np.max(extent) > 100:
        unit = "mm"
    else:
        unit = "Meter"
    print(f"Hinweis: Wenn Ihr CAD-Modell in {unit} vorliegt, beträgt der mittlere Fehler {cd_l1:.2f} {unit}.")
    
    # Visualisierung starten
    print("
-> Öffne 3D-Visualisierung. Schließen Sie das Fenster, um das Skript zu beenden.")
    pcd_gof.paint_uniform_color([1, 0, 0]) # Rot = GOF Mesh
    pcd_gt.paint_uniform_color([0, 1, 0])  # Grün = CAD Ground Truth
    o3d.visualization.draw_geometries([pcd_gof, pcd_gt], window_name="ICP Alignment Kontrolle (Rot: GOF, Grün: CAD)")

if __name__ == "__main__":
    # Pfade zu Ihren Dateien anpassen
    GOF_MESH_PATH = "gof_palette.obj"
    GT_CAD_PATH = "epal_reference.obj"
    
    # Führen Sie die Funktion aus
    # evaluate_chamfer_distance(GOF_MESH_PATH, GT_CAD_PATH)
    pass
