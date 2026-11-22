# From Reality to Simulation

**3D Reconstruction for Virtual Simulations | Bachelor's Thesis · TUM · 2026**

Can a simple smartphone video be turned into a 3D object that works in a physics simulation? This project tests a complete **real-to-sim pipeline** using an EPAL pallet — from image capture to reconstruction, mesh extraction and Unity.

## The Pipeline

![Reconstruction pipeline from the thesis](media/images/pipeline.png)

A smartphone records the pallet. The images are filtered and processed with COLMAP, reconstructed using modern splatting methods, converted to meshes and tested in Unity.

## Gaussian Splatting

![Comparison of GOF, Triangle Splatting and SuGaR](media/images/splatting-comparison.png)

*From left to right: GOF, Triangle Splatting and SuGaR (Thesis, Fig. 4-7).*

**Video showcase — add your Gaussian Splatting recording here:**

<!-- Replace this line with your GitHub-uploaded MP4 URL or a linked video thumbnail. -->

🎥 **[Watch the Gaussian Splatting demo](media/videos/gaussian-splatting-demo.mp4)** *(add video before publishing)*

## From Reconstruction to Simulation

![GOF mesh reconstruction](media/images/gof-mesh.png)

*Extracted GOF mesh from different angles (Thesis, Fig. 4-9).*

![Unity collision and physical interaction tests](media/images/unity-simulation.png)

*Collision tests in Unity (Thesis, Fig. 5-2).*

## Key Findings

- **Video + FFT filtering** provided an effective input workflow.
- **Gaussian Splatting** produced strong visual results; Triangle Splatting was less practical to integrate.
- **SuGaR and GOF** both produced usable meshes, but additional cleanup was needed.
- **Unity tests** demonstrated LiDAR detection and basic collision interactions. A visually accurate model still needs appropriate collision geometry.

## Code & Downloads

| Resource | File |
|---|---|
| Image / video frame filtering | [Filter scripts](scripts/data_filtering/) |
| Visual and geometric metrics | [Evaluation scripts](scripts/evaluation/) |
| Reconstructed 3D assets | [Models](models/) |
| Full bachelor's thesis | [Thesis PDF](docs/thesis.pdf) |

*Add the original scripts, models and thesis PDF to these folders before publishing. They are not included in this package.*

## Built With

[COLMAP](https://github.com/colmap/colmap) · [3D Gaussian Splatting](https://github.com/graphdeco-inria/gaussian-splatting) · [LightGlue](https://github.com/cvg/LightGlue) · [SuGaR](https://github.com/Anttwo/SuGaR) · [Unity Gaussian Splatting](https://github.com/aras-p/UnityGaussianSplatting) · Unity · Blender · MeshLab

---

**Bachelor's thesis:** *Investigation of Modern 3D Model Reconstruction Methods for Virtual Simulations* · Technical University of Munich, Chair of Materials Handling, Material Flow, Logistics (fml), 2026.
