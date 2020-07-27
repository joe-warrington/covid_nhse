#!/usr/bin/env python3

import copy
import datetime
import os
import wget

import numpy as np

from matplotlib import pyplot as plt
import pandas as pd


def date_to_string(datetime_in):
    month_string = ['', 'Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'August']
    return '{:d}-'.format(datetime_in.day) + month_string[datetime_in.month]


def file_datestring(datetime_in):
    return '{:04d}-{:02d}-{:02d}'.format(datetime_in.year, datetime_in.month, datetime_in.day)


region_names = ['East Of England', 'London', 'Midlands', 'North East And Yorkshire',
                'North West', 'South East', 'South West', 'England']
region_popns = [6.2, 8.9, 10.7, 8.1, 7.3, 9.1, 5.6, 56.0]
history_start = datetime.date(day=19, month=3, year=2020)
record_start = datetime.date(day=2, month=4, year=2020)
today = datetime.date.today()
now = datetime.datetime.now()
print('Current time {:02d}:{:02d}'.format(now.hour, now.minute))

# Create data and output folders if necessary
if not os.path.exists('data/'):
    os.makedirs('data')
if not os.path.exists('out/'):
    os.makedirs('out')

# Download Excel sheets from the NHS if not already stored locally.
record_range = (pd.date_range(record_start, today)
                if now.time() > datetime.time(hour=14, minute=5)
                else pd.date_range(record_start, today - datetime.timedelta(days=1)))
for d in record_range:
    fn = f'COVID-19-daily-announced-deaths-{date_to_string(d)}-2020.xlsx'
    if not os.path.exists('data/' + fn) and (d < today or (now.time() > datetime.time(hour=14, minute=5))):
        url = 'https://www.england.nhs.uk/statistics/wp-content/uploads/sites/2/2020/{:02d}/'.format(d.month if not (d.month == 5 and d.day == 28) else 6)
        print('Fetching from ' + url + fn + '...')
        wget.download(url + fn, 'data/' + fn)

# Read Excel files and build a dictionary of deaths by death date, for each report date and region.

report_date_dict_regions = [{}, {}, {}, {}, {}, {}, {}]
date_strings = [date_to_string(d) for d in record_range]
total_reported_deaths = 0
for i, date in enumerate(record_range):
    d = date_strings[i]
    sn = 'COVID19 daily deaths by region' if date <= datetime.date(2020, 5, 20) else 'Tab1 Deaths by region'
    fn = 'data/COVID-19-daily-announced-deaths-' + d + '-2020.xlsx'
    print('Reading ' + fn + '...')
    skiprows = range(14) if d == '2-April' else range(13)
    df = pd.read_excel(fn, sheet_name=sn, nrows=9, skiprows=skiprows, parse_dates=True)
    deaths_by_date_reported_here_today = {}
    deaths_reported_today = 0
    for r in range(7):
        assert df['NHS England Region'].iloc[2 + r] == region_names[r], df['NHS England Region'].iloc[2 + r]
        for column in df:
            if isinstance(column, datetime.datetime):
                if isinstance(df[column].iloc[2 + r], (int, float)) and not np.isnan(df[column].iloc[2 + r]):
                    deaths_by_date_reported_here_today[date_to_string(column)] = int(df[column].iloc[2 + r])
                    deaths_reported_today += int(df[column].iloc[2 + r])
                else:
                    deaths_by_date_reported_here_today[date_to_string(column)] = 0
                total_reported_deaths += deaths_by_date_reported_here_today[date_to_string(column)]
        report_date_dict_regions[r][d] = copy.deepcopy(deaths_by_date_reported_here_today)  # d is the report date
    print('{:0d} deaths reported today.'.format(deaths_reported_today))
manually_summed_total = sum([sum([sum(report_date_dict_regions[r][d].values())
                                  for d in report_date_dict_regions[r].keys()])
                             for r in range(7)])
print(f'Total NHSE reported deaths by report date: {total_reported_deaths}')
assert manually_summed_total == total_reported_deaths, manually_summed_total

history_range = pd.date_range(history_start, today)
date_list = [date_to_string(d) for d in history_range]

for i, end_date in enumerate(record_range):
    death_date_dict_regions = [{date: 0 for date in date_list},
                               {date: 0 for date in date_list},
                               {date: 0 for date in date_list},
                               {date: 0 for date in date_list},
                               {date: 0 for date in date_list},
                               {date: 0 for date in date_list},
                               {date: 0 for date in date_list}]
    plt.figure(figsize=(16, 12))
    for j, r in enumerate([4, 3, 2, 0, 1, 5, 6]):
        for day_d, day_d_val in report_date_dict_regions[r].items():
            if day_d not in date_strings[:i+1]:
                continue
            for date, date_val in day_d_val.items():
                if date not in death_date_dict_regions[r].keys():
                    death_date_dict_regions[r][date] = date_val
                else:
                    death_date_dict_regions[r][date] += date_val

        report_date_vals = [sum(report_date_dict_regions[r][date].values())
                            if date in report_date_dict_regions[r].keys() else 0
                            for date in date_list]
        death_date_vals = [death_date_dict_regions[r][date]
                           if date in death_date_dict_regions[r].keys() else 0
                           for date in date_list]
        plt.subplot(4, 2, j+1)
        plt.bar([x + 0.25 for x in range(len(date_list))],
                report_date_vals, 0.5, label='Report date')
        plt.bar([x - 0.25 for x in range(len(date_list))],
                death_date_vals, 0.5, label='Death date')
        plt.xticks(range(len(date_list))[::3], rotation=90)
        plt.xlim([-0.5, len(date_list) - 0.5])
        plt.ylim([0, 300 * region_popns[r] / 20.0])
        ax = plt.gca()
        ax.set_xticklabels(date_list[::3] if r == 6 else [''] * len(date_list[::3]))
        plt.title(f'Deaths by report and death date, {region_names[r]} (population {region_popns[r]}m)')
        plt.ylabel('Deaths')
        plt.legend()
        plt.grid()
    report_date_vals_total = [sum([sum(report_date_dict_regions[r][date].values())
                              if date in report_date_dict_regions[r].keys() else 0 for r in range(7)])
                              for date in date_list]
    death_date_vals_total = [sum([death_date_dict_regions[r][date]
                             if date in death_date_dict_regions[r].keys() else 0 for r in range(7)])
                             for date in date_list]
    print(f'Total by report date: {sum(report_date_vals_total)}')
    print(f'Total by death date: {sum(death_date_vals_total)}')
    plt.subplot(4, 2, 8)
    plt.bar([x + 0.25 for x in range(len(date_list))],
            report_date_vals_total, 0.5, label='Report date')
    plt.bar([x - 0.25 for x in range(len(date_list))],
            death_date_vals_total, 0.5, label='Death date')
    plt.xticks(range(len(date_list))[::3], rotation=90)
    plt.xlim([-0.5, len(date_list) - 0.5])
    ax = plt.gca()
    ax.set_xticklabels(date_list[::3])
    plt.title(f'Deaths by report and death date, {region_names[7]} (population {region_popns[7]}m)')
    plt.ylabel('Deaths')
    plt.legend()
    plt.grid()
    # plt.tight_layout()
    fn = 'out/daily_total_reports' + file_datestring(end_date) + '.pdf'
    print('Saving ' + fn + '...')
    plt.savefig(fn)
    plt.close()
