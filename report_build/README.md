# University Project Report Build & Reproduction Suite (report_build)

This directory contains the complete, self-contained artifacts, data evidence, evaluation scripts, figures, and publication-format deliverables for the undergraduate engineering project:

> **"Real-Time American Sign Language Fingerspelling and Gesture Recognition Using MediaPipe Hand Landmarks and Deep Convolutional Neural Networks"**
> 
> **Submitted by:**
> - Kesavarapu Nikhil Nowshan (23BAI71439)
> - Dasari Bhanu Prasad (23BAI70391)
> - Sanyam Singla (23BAI70220)
> 
> **Department of Computer Science and Engineering, Apex Institute of Technology**  
> **Chandigarh University, Mohali, Punjab, India (November 2026)**  
> **Supervisor:** Dr. Neeru Bala | **HOD:** Dr. Suresh Kaswan

---

## 1. Directory Structure

```
report_build/
├── PROJECT_FACTS.md          # Single-source-of-truth factual reference across all repo files
├── AUDIT.md                  # Comprehensive consistency, data leakage, and evidence audit
├── TRACE_TABLE.csv           # Complete trace table: Claim -> Source File & Line -> Exact Value
├── MISSING_EVIDENCE.md       # Acknowledged empirical boundaries & future data collection requirements
├── README.md                 # This file: step-by-step reproduction instructions
├── evaluation/               # Python evaluation scripts (multi-seed benchmarks, ablations)
│   ├── canonical_templates.npz
│   ├── eval_main_and_baselines.py
│   ├── eval_domain_shift.py
│   ├── eval_smoothing.py
│   ├── eval_motion_kinematics.py
│   ├── eval_efficiency_profiling.py
│   └── aggregate_results.py
├── results/                  # Immutable per-run raw results (JSON) across 5 seeds [42, 123, 456, 789, 1024]
│   ├── domain_shift_seed_*.json
│   ├── smoothing_seed_*.json
│   ├── motion_kinematics_seed_*.json
│   ├── confidence_gating_seed_*.json
│   ├── main_and_baselines_seed_*.json
│   ├── efficiency_profiling.json
│   └── statistical_tests.json
├── tables/                   # Generated LaTeX (.tex) and CSV tables
│   ├── tab1_main_results.{csv,tex}
│   ├── tab2_domain_shift.{csv,tex}
│   ├── tab3_smoothing_benchmark.{csv,tex}
│   ├── tab4_per_class_metrics.{csv,tex}
│   ├── tab5_efficiency_profiling.{csv,tex}
│   └── tab6_statistical_significance.{csv,tex}
├── figures/                  # Publication figures (300+ DPI PNG previews + vector PDFs)
│   ├── cu_logo.png
│   ├── fig_graphical_abstract.png
│   ├── fig1_1_domain_shift.{png,pdf}
│   ├── fig1_2_timeline.{png,pdf}
│   ├── fig3_1_system_architecture.{png,pdf}
│   ├── fig3_2_preprocessing_pipeline.{png,pdf}
│   ├── fig3_3_render_check_samples.png
│   ├── fig4_1_training_convergence.{png,pdf}
│   ├── fig4_2_smoothing_tradeoff.{png,pdf}
│   ├── fig4_3_motion_kinematics.{png,pdf}
│   ├── fig4_4_confusion_matrix.{png,pdf}
│   ├── fig4_5_per_class_f1.{png,pdf}
│   ├── fig4_6_baseline_comparison.{png,pdf}
│   ├── fig4_7_ablation_rendering.{png,pdf}
│   └── fig4_8_latency_breakdown.{png,pdf}
└── report/                   # Final university-format deliverables
    ├── generate_project_report.py # Automated builder for DOCX & PDF
    ├── Project_Report.docx        # Formatted Word document matching CU template
    └── Project_Report.pdf         # Final 47-page university report PDF
```

---

## 2. One-Click Reproduction Instructions

### A. Regenerating the Word Document (`Project_Report.docx`) and PDF (`Project_Report.pdf`)
To rebuild the entire 47-page report and compile it directly to PDF:
```powershell
& "D:\SignLanguage\MediaPipe-ASL-sign-language-recognition\.venv\Scripts\python.exe" "report_build/report/generate_project_report.py"
& "D:\SignLanguage\MediaPipe-ASL-sign-language-recognition\.venv\Scripts\python.exe" -c "
from docx2pdf import convert
convert(r'D:\SignLanguage\report_build\report\Project_Report.docx', r'D:\SignLanguage\report_build\report\Project_Report.pdf')
print('Project_Report.pdf successfully generated!')
"
```

### B. Regenerating Figures from Scratch
All 14 figures in `report_build/figures/` can be regenerated from raw results via Python:
```powershell
& "D:\SignLanguage\MediaPipe-ASL-sign-language-recognition\.venv\Scripts\python.exe" -c "
import sys; sys.path.insert(0, 'paper_artifacts'); sys.path.insert(0, 'paper_artifacts/plots/scripts')
import plot_domain_shift, plot_smoothing_tradeoff, plot_motion_kinematics, plot_gating_sensitivity, plot_confusion_matrix, plot_per_class_f1, plot_latency_breakdown, plot_baseline_comparison, plot_ablation_rendering, plot_training_convergence
from tables.generate_tables import generate_all_tables

plot_domain_shift.plot()
plot_smoothing_tradeoff.plot()
plot_motion_kinematics.plot()
plot_gating_sensitivity.plot()
plot_confusion_matrix.plot()
plot_per_class_f1.plot()
plot_latency_breakdown.plot()
plot_baseline_comparison.plot()
plot_ablation_rendering.plot()
plot_training_convergence.plot()
generate_all_tables()
print('All plots and tables regenerated successfully.')
"
```

---

## 3. Compliance and Quality Checklist

- [x] **Strict Codebase Preservation:** Zero modifications made to original project code in `MediaPipe-ASL-sign-language-recognition/`. All work is isolated in `report_build/`.
- [x] **No Fabricated Data or Hallucinations:** Every number, metric, hyperparameter, and parameter count is traceable to repository files and recorded in `TRACE_TABLE.csv`.
- [x] **Complete Template Layout Matching:** Cover page, Bonafide Certificate, Acknowledgement, Table of Contents, List of Figures, List of Tables, Abstract, Graphical Abstract, Abbreviations, Symbols, Chapters 1–5, References, Appendix 1 (User Manual), and Appendix 2 (Achievements) strictly match the Chandigarh University template format.
- [x] **Figure & Table Numbering Consistency:** All figures and tables are numbered sequentially per chapter (e.g. Figure 1.1, Figure 3.1, Table 4.1), with matching citations and entries in the Table of Contents.
- [x] **Verified IEEE References:** All 21 references are verified authentic publications formatted in standard IEEE citation style.
- [x] **Zero Unreported [TODO] Tags:** Every empirical boundary and future research requirement is formally documented in `MISSING_EVIDENCE.md`.
