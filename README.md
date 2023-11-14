# kg-lab-ws23-task3
Knowledge Graph Lab 💡 - winter semester 2023 - task 3

<img src="images/RWTH_Logo.png" width="500">

This repository embodies an approach of identifying event series for scientific events such as conferences and workshops. The unstructured event data is queried from [dblp](https://dblp.org/) and assigned to the correct event series using the code provided here. After correctly assigning the event series, the property of event series is added to the KG of Wikidata.

[![GitHub last commit](https://img.shields.io/github/last-commit/olafbombach/kg-lab-ws23-task3.svg)](https://github.com/olafbombach/kg-lab-ws23-task3/commits/main)
[![GitHub issues](https://img.shields.io/github/issues/olafbombach/kg-lab-ws23-task3.svg)](https://github.com/olafbombach/kg-lab-ws23-task3/issues)
[![GitHub issues](https://img.shields.io/github/issues-closed/olafbombach/kg-lab-ws23-task3.svg)](https://github.com/olafbombach/kg-lab-ws23-task3/issues/?q=is%3Aissue+is%3Aclosed)
![Python Version](https://img.shields.io/badge/Python-3.9%2B-brightgreen)

## Use Case Scenario
Situation:

The proceedings of the publication service CEUR-WS (CEUR Workshop Proceedings) already have entries in Wikidata, but the relation between individual proceedings is insufficient specified or missing.

Action:
<ul>
<li>Collect missing information from dblp and ceur-spt.
<li>Identify event series using Large Language Models.
<li>Validate the resulting event series.
<li>Update the Knowledge Graph.
</ul>

Expected Result:

Proceedings of the same event series are interconnected in a way such that the user is able to access the whole event series.
## Current status of the project:
<ul> 
    <li> Assessment of current KG status ❌ </li>
    <li> Preprocessing of queries ❌ </li>
    <il> (Method for encoding established) ❌ </il>
    <li> Validation of LLM (check for accuracy and precision) ❌ </li>
    <li> (Further methods of assignments established) ❌ </li>
    <li> Method for data transfer to the KG ❌ </li>
    <li> Establishment of an automated method ❌ </li>
    <li> Validation of the method ❌ </li>
</ul>

## Deadlines

- 2024-01-19: Midterm coordination
- 2024-03-22: Project result delivery
- 2024-03-29: Final presentation

## How to install the repository in your workspace:
```bash
git clone https://github.com/olafbombach/kg-lab-ws23-task3
```

## Why?
This task is part of the practical lab (KG Lab) presented by the Chair of Databases and Information Systems [(i5)](https://dbis.rwth-aachen.de/dbis/) of RWTH Aachen.

## How to contribute to this project:
Thank you for your interest in contributing to this project! We welcome all kinds of contributions, no matter how small or big they are. Whether it's adding new features, fixing bugs, improving documentation, or suggesting new ideas.
In this regard, please follow our [Code of Conduct](.github/CONTRIBUTION.md)
