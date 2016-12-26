# -*- coding: utf-8-unix -*-
"""
Usage
easy_install-2.7 pip
pip install python-gantt
"""

import datetime
import gantt

# Change font default
gantt.define_font_attributes(fill='black',
                             stroke='black',
                             stroke_width=0,
                             font_family="Verdana")

# Add vacations for everyone
gantt.add_vacations(datetime.date(2016, 1, 1))
gantt.add_vacations(datetime.date(2016, 1, 11))

# Create two resources
A = gantt.Resource('佐藤')
B = gantt.Resource('B')
C = gantt.Resource('C')

# Add vacations for one lucky resource
A.add_vacations(
    dfrom=datetime.date(2016, 1, 4), 
    dto=datetime.date(2016, 1, 5) 
    )
B.add_vacations(
    dfrom=datetime.date(2016, 1, 4), 
    dto=datetime.date(2016, 1, 4), 
    )


# Create some tasks
one_day = datetime.timedelta(days=1)
all_sd = gantt.Task(name='all',
                start=datetime.date(2016, 1, 4),
                duration=8,
                resources=[A])
f1_sd = gantt.Task(name='f1_sd',
                start=datetime.date(2016, 1, 4),
                duration=4,
                resources=[C])
f1_pg = gantt.Task(name='f1_pg',
                start=datetime.date(2016, 1, 8),
                duration=3,
                resources=[C])
f1_mt = gantt.Task(name='f1_mt',
                start=datetime.date(2016, 1, 14),
                duration=5,
                percent_done=50)
f2_sd = gantt.Task(name='f2_sd',
                start=f1_sd.end_date() + one_day,
                duration=4,
                resources=[C])


# Create a project
p1 = gantt.Project(name='Projet 1')

# Add tasks to this project
p1.add_task(all_sd)
p1.add_task(f1_sd)
p1.add_task(f1_pg)
p1.add_task(f1_mt)
p1.add_task(f2_sd)

p = gantt.Project(name='Gantt')
# wich contains the first two projects
# and a single task
p.add_task(p1)



##########################$ MAKE DRAW ###############
p.make_svg_for_tasks(filename='test_full.svg',
                     start=datetime.date(2016, 01, 1),
                     end=datetime.date(2016, 02, 29))
##########################$ /MAKE DRAW ###############
