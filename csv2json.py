#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  csv2json.py
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
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
import csv, json, time

dayKey = {0 : 'Mo', 1 : 'Tu', 2 : 'We', 3 : 'Th', 4 : 'Fr', 5 : 'Sa', 6 : 'Su'}

def readCsvFile(fileName):
    
    stops = []
    
    with open(fileName, newline='') as FileCsv:
        reader = csv.reader(FileCsv)
        next(reader, None)
        for row in reader:
            stop = readRow(row)
            stops.append(stop)
            
    return stops
            
def readRow(row):
    
    data = {'ref' : row[0],
             'from' : row[1],
             'services' : [serviceDays([row[2], row[3], row[4], row[5], row[6], row[7], row[8]])],
             'trip' : row[9],
             'stations': [row[10]],
             'times' : [row[11]],
             'to' : row[12]}
             
    return data
    
def serviceDays(days):
    
    start = 0
    weekDays = 7
    while start < weekDays and days[start] == '0':
            start += 1
    end = start
    while end < weekDays-1 and days[end+1] == '1':
        end += 1
    if start == end:
        services = dayKey[start]
    else:
        services = dayKey[start] + '-' + dayKey[end]
    
    return services
    
def giveJsonFormat(stops):
    
    trips = groupTrips(stops)
    routes = groupRoutes(trips)
    services = groupByReference(routes)
    
    return services
    
def groupByReference(routes):
    
    services = []
    
    for route in routes:
        servicePosition = searchReference(route, services)
        services = addRoute(route, services, servicePosition)
    
    return services
    
def searchReference(route, services):
    
    size = len(services)
    position = -1
    service = 0
    
    while service < size:
        currentService = services[service]
        if currentService[0] == route['ref']:
            position = service
            service = size+1
        else:
            service += 1
            
    return position
    
def addRoute(route, services, servicePosition):
    
    if servicePosition == -1:
        services.append([route['ref'],
                        [{'from' : route['from'],
                                      'services' : route['services'],
                                      'stations' : route['stations'],
                                      'times' : route['times'],
                                      'to' : route['to']}]])
    else:
        services[servicePosition][1].append({'from' : route['from'],
                                                     'services' : route['services'],
                                                     'stations' : route['stations'],
                                                     'times' : route['times'],
                                                     'to' : route['to']})
    
    return services
    
def groupRoutes(trips):
    
    routes = []
    
    for trip in trips:
        routePosition = searchRoute(trip, routes)
        routes = addTrip(trip, routes, routePosition)
    
    return routes
    
def searchRoute(trip, routes):
    
    size = len(routes)
    position = -1
    route = 0
    
    while route < size:
        currentRoute = routes[route]
        if trip['from'] == currentRoute['from'] and trip['to'] == currentRoute['to'] and trip['ref'] == currentRoute['ref'] and trip['services'][0] == currentRoute['services'][0]:
            position = route
            route = size+1
        else:
            route += 1
            
    return position
    
def addTrip(trip, routes, routePosition):
    
    if routePosition == -1:
        trip['times'] = [trip['times']]
        routes.append(trip)
    else:
        routes[routePosition]['times'].append(trip['times'])
    
    return routes
    
def groupTrips(stops):
    
    trips = []
    
    for stop in stops:
        tripPosition = searchTrip(stop, trips)
        trips = addStop(stop, trips, tripPosition)
    
    return trips
    
def searchTrip(stop, trips):
    
    size = len(trips)
    position = -1
    trip = 0
    
    while trip < size:
        currentTrip = trips[trip]
        if stop['from'] == currentTrip['from'] and stop['to'] == currentTrip['to'] and stop['trip'] == currentTrip['trip'] and stop['services'][0] == currentTrip['services'][0]:
            position = trip
            trip = size+1
        else:
            trip += 1
            
    return position

def addStop(stop, trips, tripPosition):
    
    if tripPosition == -1:
        trips.append(stop)
    else:
        trips[tripPosition]['stations'].append(stop['stations'][0])
        trips[tripPosition]['times'].append(stop['times'][0])
    
    return trips
    
def writeJsonFile(services):
    
    timesTable = generateTimesTable(services)
    timesTableFormat = json.dumps(timesTable, indent=4, ensure_ascii=False)
    
    with open("timestable.json", "w") as jsonFile:
        jsonFile.write(timesTableFormat)

def generateTimesTable(services):
    ref = 0
    timesTable = {'update': time.strftime('%d.%m.%Y'),
             'lines' : {}}
    for service in services:
        if service[ref] not in timesTable['lines']:
            timesTable['lines'][service[ref]] = service[1]
        else:
            timesTable['lines'][service[ref]].append(service[1]) 
    return timesTable
    
def csv2json(filename):
    stops = readCsvFile(filename)
    services = giveJsonFormat(stops)
    writeJsonFile(services)
    

def main(args):
    csv2json(args)
    
    return 0

if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    if len(sys.argv) == 2 and '.csv' in filename: 
        sys.exit(main(filename))
    else:
        print('No such file found, make sure you are using a valid file ' )
