# Programmers' Visual Attention on Function Call Graphs During Code Summarization (Replication)

**Repository:** [https://github.com/AgentBubu/CallGraph-ReproNew](https://github.com/AgentBubu/CallGraph-ReproNew)

This repository contains the data and code necessary to replicate the analysis from the paper *Programmers' Visual Attention on Function Call Graphs During Code Summarization*. 

## Project Setup & Java Repositories

The original Google Drive link containing the target Java projects is no longer active. To recreate the `PROJECTS_DIR` required for the pre-processing scripts to run, you must clone the original open-source repositories locally.

Run the following commands in your terminal to download the required project codebases:

```bash
git clone [https://github.com/sksamuel/scrimage.git](https://github.com/sksamuel/scrimage.git)
git clone [https://github.com/mimno/Mallet.git](https://github.com/mimno/Mallet.git) mallet
git clone [https://github.com/openaudible/openaudible.git](https://github.com/openaudible/openaudible.git)
git clone [https://github.com/FreeCol/freecol.git](https://github.com/FreeCol/freecol.git)
git clone https://github.com/yinlou/mltk.git
```

## Pre-Processing Instructions
The fixation data (converted to CSV format using the iTrace Toolkit) is located in the `PreProcessedData_CallGraphVisualAttention` folder. This includes data from Study 1 (participant numbers < 20) and Study 2 (participant numbers > 20).

1. Locate the `call_graphs` folder within `PreProcessedData_CallGraphVisualAttention`. This contains the .txt files with call graphs for all methods, as well as the participant summaries and reviewer ratings (study1_summaries.csv and study2_summaries.csv).
2. Open `constants.py` in your code editor.
3. Set the `DATA_DIR` variable to the path of the `PreProcessedData_CallGraphVisualAttention` folder.
4. Set the `PROJECTS_DIR` variable to the path of the folder where you cloned the Java projects in the previous setup step.

## Analysis Steps
Execute the following scripts in order to replicate the data processing and analysis:

1. Run `step_1_data_processing.py`
Combines summary and confidence ratings with the fixation data. Saves the output to the Processed Data folder.

2. Run `step_2_annotate_methods.py`
Annotates each fixation with the name of the method being fixated on. Fixations occurring outside method bounds are marked as "no method".

3. Run `step_3_generate_metrics.py`
Calculates the core graph metrics for each trial (node coverage, weighted node coverage, edge coverage, weighted edge coverage, average fixation duration, number of fixations, and max depth) using coverage_metrics.py and call_graph_builder.py. Outputs are saved to the output folder.

4. Run `step_4_analysis.py`
Performs statistical analysis across both studies and the combined dataset. This script executes the following:
- Calculates the average proportion of methods in each project found in the call graph of each summarized method.
- Calculates the average fixation position of each code category (callee, caller, non-call graph, etc.).
- Calculates the proportion of time spent fixating on each code category.
- Computes mean and average depth statistics.
- Prepares and exports the formatted data as CSV files for regression analysis.

5. Run `step_5_regression.Rmd`
Open and execute this R Markdown file to perform the mixed-effect regression analyses. This generates the final results relating the call graph coverage metrics to the dependent variables (summary scores, confidence, and absolute confidence difference).
