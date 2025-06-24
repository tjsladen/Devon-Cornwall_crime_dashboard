# Crime Dashboard: Devon & Cornwall

An interactive dashboard built with Streamlit that explores crime trends across Devon and Cornwall by LSOA from 2022–2025.
View here: [Crime Dashboard](https://crimeapppy-78o46ocybjq6p7qxd3az2i.streamlit.app/)
## Features

- 📊 Crime counts over time and by type
- 🗺️ Interactive crime map by LSOA
- 🥧 Crime outcome and type distribution per year
- Comparison of multiple LSOAs over time

## Data Sources and Licensing

This project uses public sector data from:

- [UK Police Crime Data](https://data.police.uk/data/)
- [ONS Geography Portal](https://geoportal.statistics.gov.uk/)

These data sources are licensed under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

- **Code**: Licensed under the [MIT License](LICENSE)

## Run Locally

```bash
pip install -r requirements.txt
streamlit run crime_app.py
