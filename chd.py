from uk_covid19 import Cov19API
from matplotlib import pyplot as plt

RECENT_DAYS_EXCLUDED = 3
HOSP_LAG = 7
DEATH_LAG = 14

england_only = [
    'areaType=nation',
    'areaName=England'
]

cases_and_deaths = {
    "date": "date",
    "areaName": "areaName",
    "areaCode": "areaCode",
    "newCasesBySpecimenDate": "newCasesBySpecimenDate",
    "newAdmissions": "newAdmissions",
    "hospitalCases": "hospitalCases",
    "newDeaths28DaysByDeathDate": "newDeaths28DaysByDeathDate",
}

api = Cov19API(filters=['areaType=overview'], structure=cases_and_deaths)

data = api.get_dataframe()

print(data.head(10))
plt.figure()
ax = plt.gca()
ax.plot(data['date'].tolist()[-1:RECENT_DAYS_EXCLUDED:-1], data['newCasesBySpecimenDate'].tolist()[-1:RECENT_DAYS_EXCLUDED:-1], label="Cases")
ax.plot(data['date'].tolist()[-1:RECENT_DAYS_EXCLUDED+HOSP_LAG:-1], data['newAdmissions'].apply(lambda x: x * 20).tolist()[-1-HOSP_LAG:RECENT_DAYS_EXCLUDED:-1], label="Admissions * 20")
ax.plot(data['date'].tolist()[-1:RECENT_DAYS_EXCLUDED+DEATH_LAG:-1], data['newDeaths28DaysByDeathDate'].apply(lambda x: x * 50).tolist()[-1-DEATH_LAG:RECENT_DAYS_EXCLUDED:-1], label="Deaths * 50")
plt.legend()

dates = data['date'].tolist()[-1:RECENT_DAYS_EXCLUDED+DEATH_LAG:-1]
cases = data['newCasesBySpecimenDate'].tolist()[-1:RECENT_DAYS_EXCLUDED+DEATH_LAG:-1]
a_shifted = data['newAdmissions'].tolist()[-1-HOSP_LAG:RECENT_DAYS_EXCLUDED+DEATH_LAG-HOSP_LAG:-1]
d_shifted = data['newDeaths28DaysByDeathDate'].tolist()[-1-DEATH_LAG:RECENT_DAYS_EXCLUDED:-1]

cases_per_a = [c / a_shifted[i] for i, c in enumerate(cases)]
d_per_case = [100 * d_shifted[i] / c if c > 0 else 0 for i, c in enumerate(cases)]
d_per_a = [100 * d / a_shifted[i] for i, d in enumerate(d_shifted)]
plt.figure()
plt.subplot(311)
plt.plot(dates, cases_per_a)
plt.ylabel('Cases/admission')
plt.subplot(312)
plt.plot(dates, d_per_case)
plt.ylabel('Case fat. rate (%)')
plt.ylim([0, 4.0])
plt.subplot(313)
plt.plot(dates, d_per_a)
plt.ylabel('Hosp. fat. rate (%)')
plt.show()
