#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  csv2timestable.py
#  
#  Copyright 2019 Laboratorio Experimental 04 <labexp04@labexp04>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  
import csv, json, time

#Diccionary of keywords to make a field stations
day_key = {0 : 'Mo', 1 : 'Tu', 2 : 'We', 3 : 'Th', 4 : 'Fr', 5 : 'Sa', 6 : 'Su'}
keys = {'ref': 0, 'from': 1, 'monday': 2, 'tuesday': 3, 'wednesday': 4, 'thursday': 5, 'friday': 6, 'saturday': 7, 'sunday': 8,
        'trip': 9, 'stations': 10, 'times': 11, 'to': 12}

#Read a CSV file and load stops in memory
def read_csv_file(file_name):

    stops = []

    with open(file_name, newline='') as File_csv:
        reader = csv.reader(File_csv)
        next(reader, None)
        for row in reader:
            stop = read_row(row)
            stops.append(stop)

    return stops

#Process a row of CSV file
def read_row(row):

    data = {'ref' : row[keys['ref']],
             'from' : row[keys['from']],
             'services' : [service_days([row[keys['monday']], row[keys['tuesday']], row[keys['wednesday']],
                                        row[keys['thursday']], row[keys['friday']], row[keys['saturday']], row[keys['sunday']]])],
             'trip' : row[keys['trip']],
             'stations': [row[keys['stations']]],
             'times' : [row[keys['times']]],
             'to' : row[keys['to']]}

    return data

#Agroup routes services days
def service_days(days):

    start = 0
    week_days = 7
    while start < week_days and days[start] == '0':
            start += 1
    end = start
    while end < week_days-1 and days[end+1] == '1':
        end += 1
    if start == end:
        services = day_key[start]
    else:
        services = f'{day_key[start]}-{day_key[end]}'

    return services

# Receive stops  and create a structure of services in memory
def give_json_format(stops):

    trips = group_trips(stops)
    routes = group_routes(trips)
    services = group_by_reference(routes)

    return services

#From stops create trips
def group_trips(stops):

    trips = []

    for stop in stops:
        trip_position = search_trip(stop, trips)
        trips = add_stop(stop, trips, trip_position)

    return trips

#Localize if a trip exist in the structure and if not returns -1
def search_trip(stop, trips):

    size = len(trips)
    position = -1
    trip = 0

    while trip < size:
        current_trip = trips[trip]
        if stop['from'] == current_trip['from'] and stop['to'] == current_trip['to'] and stop['trip'] == current_trip['trip'] and stop['services'][0] == current_trip['services'][0]:
            position = trip
            trip = size+1
        else:
            trip += 1

    return position

#Merge stops with the same trip
def add_stop(stop, trips, trip_position):

    if trip_position == -1:
        trips.append(stop)
    else:
        trips[trip_position]['stations'].append(stop['stations'][0])
        trips[trip_position]['times'].append(stop['times'][0])

    return trips

#From trips create routes
def group_routes(trips):

    routes = []

    for trip in trips:
        route_position = search_route(trip, routes)
        routes = add_trip(trip, routes, route_position)

    return routes

#Localize if a route exist in the structure and if not returns -1
def search_route(trip, routes):

    size = len(routes)
    position = -1
    route = 0

    while route < size:
        current_route = routes[route]
        if trip['from'] == current_route['from'] and trip['to'] == current_route['to'] and \
                trip['ref'] == current_route['ref'] and trip['services'][0] == current_route['services'][0]:
            position = route
            route = size+1
        else:
            route += 1

    return position

#Merge trips of the same route
def add_trip(trip, routes, route_position):

    if route_position == -1:
        trip['times'] = [trip['times']]
        routes.append(trip)
    else:
        routes[route_position]['times'].append(trip['times'])

    return routes

#From routes and references create services
def group_by_reference(routes):

    services = []

    for route in routes:
        service_position = search_reference(route, services)
        services = add_route(route, services, service_position)

    return services

#Localize if a services exist in the structure and if not returns -1
def search_reference(route, services):

    size = len(services)
    position = -1
    service = 0

    while service < size:
        current_service = services[service]
        if current_service[0] == route['ref']:
            position = service
            service = size+1
        else:
            service += 1

    return position

#Merge routes with the same reference
def add_route(route, services, service_position):

    if service_position == -1:
        services.append([route['ref'],
                        [write_service(route)]])
    else:
        services[service_position][1].append(write_service(route))

    return services

#
def write_service(route):
    service = {'from': route['from'],
               'services': route['services'],
               'stations': route['stations'],
               'times': route['times'],
               'to': route['to']}
    return service


#Write data to a Json file
def write_json_file(services):

    timestable = generate_timestable(services)
    timestable_format = json.dumps(timestable, indent=4, ensure_ascii=False)

    with open("timestable.json", "w") as json_file:
        json_file.write(timestable_format)

#Create a structure with the format of timestable.json
def generate_timestable(services):
    ref = 0
    timestable = {'update': time.strftime('%d.%m.%Y'),
             'lines' : {}}
    for service in services:
        if service[ref] not in timestable['lines']:
            timestable['lines'][service[ref]] = service[1]
        else:
            timestable['lines'][service[ref]].append(service[1])
    return timestable

#The script main funtion
def csv2timestable(filename):
    stops = read_csv_file(filename)
    services = give_json_format(stops)
    write_json_file(services)


def main(args):
    filename = args.document
    if '.csv' in filename:
        csv2timestable(filename)
    else:
        print('No such file found, make sure you are using a valid file ')
    return 0

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Script to make timestable.json.')
    parser.add_argument("document", help="Insert a .csv document")
    args = parser.parse_args()
    main(args)