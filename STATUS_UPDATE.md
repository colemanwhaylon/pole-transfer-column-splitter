Based on the sources provided, here is an update on the current standing of the project, what remains to be done, and the plan to tackle the remaining challenges.

The primary goal of this project is to create an **automation** that pulls a weekly production report from Ox (Operation Execution System) and formats it exactly as needed for submission to Comcast, thereby eliminating the current time-consuming manual process that can take up to three hours. The project has been assigned to Max.

---

### Where the Project Stands Today

The project is currently in the **definition and initial planning phase**, with key requirements established and essential setup steps completed:

1.  **Final Product Defined:** The required format of the final report, including necessary columns (Date, Job, Engine Number, Pole Number, Notes, Tech Notes) and the exclusion of most billing codes (except trip charges), has been clearly defined. A final product example was provided to Max for reference.
2.  **Data Source Mapped:** The exact steps to manually pull the initial raw report from Ox were documented: navigating to the BSR PT project, selecting "reporting of quantities," and choosing "Quantities with sub and customer rates" for the appropriate date range.
3.  **Date Logic Established:** The reporting period runs from Sunday to Saturday, covering the period **three weeks back** from the Monday run date. This logic was converted into an automation formula: subtract 22 days from the current date for the beginning date, and subtract 15 days for the ending date.
4.  **Notes Issue Addressed:** The critical problem of missing Tech Notes in the standard report has been elevated; a request has been placed with Ox developers (the "headquarters") to add the notes directly to the "reporting of quantities" report.
5.  **Team and Access:** Max has been assigned to build the automation. The necessary Ox login information has been shared (username: cudd, password: Construction exclamation one).

---

### Remaining Work and Challenges

While much of the project structure is defined, there are significant data manipulation tasks and a dependency on the notes addition:

#### 1. Data Splitting and Parsing (The Major Challenge)
The biggest challenge that requires specific technical expertise is dealing with the raw data column in the Ox report which often **conjoins the marker name, engine number, and pole number**.

*   **Extraction Difficulty:** The engine number is consistently seven digits and appears first. However, the column sometimes includes the marker name (like "Pole Transfer"). The Pole Number is of a variable length. The automation must be able to parse this combined data and split it into three separate columns: Marker Name, Engine Number, and Pole Number.
*   **Variable Marker Names:** The raw data may contain various marker names like "Plant Repair," "Power Supply," or "Pole Transfer," and the automation needs to be programmed to recognize all possible types, which Delaney offered to provide a list of.

#### 2. Duplicate Removal and Filtering
The automation must accurately **remove duplicate pole entries** to avoid skewing production metrics.

*   **Logic Requirement:** Because multiple codes can be billed against a single pole, the pole details can populate multiple times on the raw report. The solution requires separating the Engine Number and Pole Number first, and then removing duplicates based solely on the Pole Number column.
*   **Trip Charge Exception:** The only billing code that needs to be explicitly noted in the final report is the "trip charge" (QMISC1/QCON15).

#### 3. General Automation Implementation
Other tasks required to complete the automation include:

*   **Column Deletion:** Deleting numerous unnecessary columns from the raw Ox report, which is considered the "very easy" portion of the task.
*   **Notes Integration:** Waiting for and then integrating the notes functionality once Ox has updated the reporting of quantities report.
*   **Final Testing:** Using the provided 10/26 to 11/1 report pull for initial testing and validation.

---

### How to Plan to Tackle It

Max and Ed have outlined a plan focused on leveraging technical solutions for the complex splitting challenge and implementing the straightforward steps first.

1.  **Immediate Implementation (Easy Parts First):** Max should begin by creating the automation activities to **pull the raw report** and **delete the unnecessary columns**. This gets the "easy" work completed rapidly.
2.  **Advanced Column Splitting:** Max plans to use **regular expressions** to handle the complex extraction and splitting of the combined marker/engine/pole column. Max may consult Evan for expertise on regular expressions if needed.
3.  **Refining Filtering Logic:** The automation will utilize the calculated date ranges (minus 22 and minus 15 days) and will implement filtering rules to ensure only unique pole entries remain, while preserving trip charge codes and their corresponding notes.
4.  **Collaboration and Support:** Max is situated in the same building as Delaney, allowing for easy access to clarify complex or variable requirements throughout the build process. Ed offered to assist Max with column manipulation strategies.
5.  **Timeline Expectation:** The automation is not expected to be ready for the upcoming Monday's report run, meaning Delaney will likely have to perform the manual process one more time. The goal is to have the automation ready for the subsequent week.

---
The overall project is characterized as "90% easy" with one main "10%" challenge regarding the column splitting, which will require specialized technical handling. Once the automation is complete, it is expected to save Delaney approximately 12 hours a month.