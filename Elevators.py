# -*- coding: utf-8 -*-
"""
Created on Sun Apr 28 00:33:44 2013

@author: finbar


    Create three classes: Building, Elevator, and Customer.

    Equip the building with an elevator. Ask user to customize the number of
    floors and the number of customers.

    Program should have error checking to make sure the user inputs are
    valid. For example, if a user gives non-integer inputs, notify the user
    that the inputs are incorrect and prompt again.

    Each customer starts from a random floor, and has a random destination
    floor.

    Each customer will use the elevator only once, i.e., when a customer
    moves out of the elevator, he/she will never use it again.

    When all customers have reached their destination floor, the simulation
    is finished.

    Part of the grade on this assignment will be the appropriateness of your
    classes, methods, and any functions you use. The quality of the code
    will now matter as well as the performance.

    All classes’ methods require a docstring for a general description of
    the method.

    Implement both your own strategy and the default strategy and compare.
    Your strategy does not have to be better but the comparison is required.

    Don’t use any global variables.

"""
from random import randint

try:
    import curses
except ImportError:
    print("""
        Curses has to be run in bash/linux, it is not dos/windows compatible.
        This program will now exit.
    """)
    import os
    os._exit(0)

import time


class Customer():
    '''
    customer is a person in the building with an int(position) and
    int(destination). Can call and direct elevators.
    '''
    def __init__(self, position, destination):

        self.position = position
        self.destination = destination

    def __str__(self):

        return "(p: %d, d: %d)" % (self.position, self.destination)

    def call_elevator(self, elevator_bank):
        '''
        function to call elevator to his location. elevator_bank is a class
        that contains all the calls for elevators
        '''
        elevator_bank.calls.append(self)
        return elevator_bank.calls

    def choose_floor(self, elevator):
        '''
        function to direct elevator to his distination
        '''
        elevator.destination = self.destination


class Elevator():
    '''
    has a list of customers in the elelvator, elevator recieves call from the
    elevator bank, his destination changes, and he moves to his destination.
    when he is al his destination he collects his caller and takes them to
    there destination.
    '''
    def __init__(self, id_=0):

        self.id_ = str(id_)
        self.occupants = []
        self.position = 0
        self.destination = 0
        self.is_free = True
        self.call = 0

    def __str__(self):

        return "[%d]" % (len(self.occupants))

    def move(self):
        '''
        function to move the lift in the required direction
        '''
        if self.destination > self.position:
            self.position += 1
        elif self.destination < self.position:
            self.position += -1
        else:
            pass

    def exit_lift(self, floor):
        '''
        function to let off customers at the this location who need to get off
        at this location. returns the number of customers to exit the lift
        floor is a list of customers on the floor
        '''
        exited = 0

        for person in self.occupants:
            if person.destination == self.position:
                floor.append(person)
                self.occupants.remove(person)
                self.call = 0
                self.is_free = True
                exited += 1

        return exited

    def board_lift(self, floor):
        '''
        function to board the caller. floor is a list of customers on the floor
        '''
        #clone taken to prevent index out of range on the loop
        #after removing people from that floor in the building
        floor_clone = floor[:]

        for person in floor_clone:
            if person == self.call:
                self.occupants.append(person)
                person.choose_floor(self)
                floor.remove(person)


class Elevator_bank():
    '''
    handles all the elevators in the buinding, has a list of elelvators,
    a Queue of calls, it gives out the jobs to the lifts, tracks quaintity
    of people moved, and knows how many floors are in the building
    '''
    def __init__(self, num_of_elevators, num_of_floors):

        self.elevators = [Elevator(i) for i in range(num_of_elevators)]
        self.num_of_floors = num_of_floors
        self.calls = []
        self.people_moved = 0

    def __str__(self):

        output = ""

        for i in range(len(self.num_of_floors)):
            output += self.print_floor(i)

        return output

    def print_floor(self, floor_id):
        '''
        outputs a text sting representation of the elevator bank on that floor.
        int(floor_id) is the floor you want to print
        '''
        output = ""

        for elevator in self.elevators:
            if elevator.position == floor_id:
                output += "|%2s|" % elevator
            else:
                output += "|   |"

        return output

    def move_lifts(self):
        '''
        calls the elevaor.move() function for every lift in the bank
        '''
        for elevator in self.elevators:
            elevator.move()

    def give_job(self, call):
        '''
        takes a job (call) and finds a lift to take the job. returns true is a
        lift was found to take the job.
        '''
        for elevator in self.elevators:
            if elevator.is_free:
                elevator.destination = call.position
                elevator.is_free = False
                elevator.call = call
                self.calls.remove(call)

                return True

    def arrivals(self, building):
        '''
        if an elelvator has arrived at its destination it take people on that
        match its call and lets people off at there destination
        '''
        for elevator in self.elevators:
            if elevator.position == elevator.destination:
                    exited = elevator.exit_lift(
                        building.floors[elevator.position]
                    )
                    elevator.board_lift(
                        building.floors[elevator.position]
                    )
                    self.people_moved += exited

    def get_data(self):
        '''
        returns a string of data on the status of every elelvator, how many
        calls left to answer and how many people have arrived at there
        destinations
        '''
        data = ""

        for elevator in self.elevators:
            data += "Elevator ID: %s Position: %s Destination: %s " % (
                elevator.id_,
                str(elevator.position),
                str(elevator.destination)
            )
            if len(elevator.occupants) > 0:
                data += "Occupant: %s\n" % (
                    elevator.occupants[0]
                )
            else:
                data += "\n"

        data += "People arrived at their destinations: %s\n" % (
            str(self.people_moved)
        )
        data += "Calls left to answer: %s\n" % (str(len(self.calls)))

        return data

    def elevators_busy(self):
        '''
        returns true if there's at least one busy elevator
        '''
        for elevator in self.elevators:
            if not elevator.is_free:
                return True


class Building():
    '''
    building has a list of lists floors, each contain customers at random.
    has an elevator bank with "n" elevators in it.
    '''
    def __init__(self, floors=0, customers=0, num_of_elevators=0):

        self.elevator_bank = Elevator_bank(num_of_elevators, floors)
        self.floors = [list() for i in range(floors)]
        self.customers = customers

    def __str__(self):
        '''
        returns a text string representation of the building, displaying each
        floor, their populations, and the elelvator bank.
        '''

        output_str = ""

        for i in range(len(self.floors) - 1, -1, -1):
            output_str += ((
                "Level:%d Population:%4d|%s" % (i, len(self.floors[i]),
                self.elevator_bank.print_floor(i))
            ))
            output_str += "\n"

        output_str += "------------------------"

        for elevator in self.elevator_bank.elevators:
            output_str += "| %s |" % elevator.id_

        output_str += "\n"

        return output_str

    def spawn_customers(self):
        '''
        randomly places a customer around the building for every customers
        thats meant to be in the building
        '''
        for i in range(0, self.customers):
            while True:
                position = randint(0, len(self.floors) - 1)
                destination = randint(0, len(self.floors) - 1)
                if position == destination:
                    continue
                else:
                    self.floors[position].append(
                        Customer(position, destination)
                    )
                    break

    def to_screen(self, screen, data):
        '''
        changes the frame and outputs it to the screen.
        '''
        time.sleep(1)
        screen.erase()
        screen.addstr(str(self))
        screen.addstr(data)
        screen.refresh()

    def to_file(self, output_file, data):
        '''
        pastes the current frame to a file
        '''
        output_file.write(str(self))
        output_file.write(data)
        output_file.write("---------------------------------------------------"
                          "------------------------------------------------\n")


def run_cycle(building, screen, output_file):
    '''
    handles everything that needs to happen in a cycle. a cycle involes
    moving, people boring or exiting lifts, new jobs assigned, frame put
    to screen and text file.
    '''
    building.elevator_bank.arrivals(building)
    data = building.elevator_bank.get_data()
    building.elevator_bank.move_lifts()
    building.to_screen(screen, data)
    building.to_file(output_file, data)


def simulate(building):
    '''
    simulates a building with elevatos and customers. takes a call from each
    customer and sends a lift to collect them. customers are moved one at a
    time per lift to there destinations. outputs the status of the building
    to a file and the screen on every loop
    '''
    data = ""
    output_file = open("elevators.txt", 'w')
    building.to_file(output_file, data)

    screen = curses.initscr()
    building.to_screen(screen, data)

    for floor in building.floors:
        for person in floor:
            if person.destination != building.floors.index(floor):
                person.call_elevator(building.elevator_bank)
    #clone taken to prevent index out of range on the loop
    #after removing calls from the calls queue
    clone_calls = building.elevator_bank.calls[:]

    for call in clone_calls:
        job_actioned = False
        while not job_actioned:
            data = ""
            job_actioned = building.elevator_bank.give_job(call)
            run_cycle(building, screen, output_file)

    while building.elevator_bank.elevators_busy():
        run_cycle(building, screen, output_file)

    time.sleep(3)
    output_file.close()
    curses.endwin()


def get_input(prompt_input, max_value, min_value, bad_input):
    '''
    handles user input read in from the console. Ensures appropriate input
    recieved
    '''

    while True:

        try:
            input_value = int(input(prompt_input))

            if input_value < min_value:
                print("Number too small")
            elif input_value <= max_value:
                break
            else:
                print(bad_input)
        except ValueError:
            print("Oops!  That was not a valid number. Please try again...")

    return input_value


def main():
    '''
    prompts user for input, instantiate the building, fills it with customers and
    runs elevator simulation.
    '''
    floors = get_input(
        "Please enter the number of floors, can't be more "
        "than 10, must be more than 1:\n",
        10,
        2,
        "You can't have that many floors, must be 10 or less\n"
    )

    customers = get_input(
        "Please enter the number of customers, can't be "
        "more than 9999, can't be zero:\n",
        9999,
        1,
        "You can't have that many customers, must be 10 or less\n"
    )

    elevators = get_input(
        "Please enter the number of elevators, can't be "
        "more than 10, can't be zero:\n",
        10, 1,
        "You can't have that many elevators, must be 5 or less\n"
    )

    my_building = Building(floors, customers, elevators)
    my_building.spawn_customers()
    simulate(my_building)

if __name__ == "__main__":
    main()
