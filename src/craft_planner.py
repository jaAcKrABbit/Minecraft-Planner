import json
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time
from heapq import heappop, heappush
from math import inf

Recipe = namedtuple('Recipe', ['name', 'check', 'effect', 'cost'])


class State(OrderedDict):
    """ This class is a thin wrapper around an OrderedDict, which is simply a dictionary which keeps the order in
        which elements are added (for consistent key-value pair comparisons). Here, we have provided functionality
        for hashing, should you need to use a state as a key in another dictionary, e.g. distance[state] = 5. By
        default, dictionaries are not hashable. Additionally, when the state is converted to a string, it removes
        all items with quantity 0.

        Use of this state representation is optional, should you prefer another.
    """

    def __key(self):
        return tuple(self.items())

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.__key() < other.__key()

    def copy(self):
        new_state = State()
        new_state.update(self)
        return new_state

    def __str__(self):
        return str(dict(item for item in self.items() if item[1] > 0))


def make_checker(rule):
    # Implement a function that returns a function to determine whether a state meets a
    # rule's requirements. This code runs once, when the rules are constructed before
    # the search is attempted.

    def check(state):
        # This code is called by graph(state) and runs millions of times.
        # Tip: Do something with rule['Consumes'] and rule['Requires'].
        if 'Consumes' in rule:
            for item in rule['Consumes']:
                #if need more than already have
                if state[item] < rule['Consumes'][item]:
                    return False

        if 'Requires' in rule:
            for require in rule['Requires']:
                #if currently doesn't meet the requirement
                if state[require]  < 1:
                    return False

        return True

    return check


def make_effector(rule):
    # Implement a function that returns a function which transitions from state to
    # new_state given the rule. This code runs once, when the rules are constructed
    # before the search is attempted.

    def effect(state):
        # This code is called by graph(state) and runs millions of times
        # Tip: Do something with rule['Produces'] and rule['Consumes'].
        # next state is based on current state
        next_state = state.copy()
        #rule['Produces']
        for product in rule['Produces']:
            next_state[product] += rule['Produces'][product]
        #rule['Consumes']
        if 'Consumes' in rule:
            for item in rule['Consumes']:
                next_state[item] -= rule['Consumes'][item]
        return next_state

    return effect


def make_goal_checker(goal):
    # Implement a function that returns a function which checks if the state has
    # met the goal criteria. This code runs once, before the search is attempted.

    def is_goal(state):
        # This code is used in the search process and may be called millions of times.
        for item in goal:
          #  print("Item in goal", item)
            if state[item] < goal[item] or item not in state:
                return False
        return True

    return is_goal


def graph(state):
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.
    for r in all_recipes:
        if r.check(state):
            yield (r.name, r.effect(state), r.cost)


def heuristic(state):
    # Implement your heuristic here!
    # don'need them
    if state['iron_axe'] > 0: 
        return inf
    if state['stone_axe'] > 0:
        return inf
    if state['wooden_axe'] > 0: 
        return inf
    # as long as we got one we good
    if state['wood'] > 1:
        return inf
    if state['bench'] > 1:
        return inf
    if state['wooden_pickaxe'] > 1: 
        return inf
    if state['coal'] > 1:
        return inf
    if state['ore'] > 1: 
        return inf
    if state['furnace'] > 1: 
        return inf
    if state['stone_pickaxe'] > 1:
        return inf
    if state['iron_pickaxe'] > 1: 
        return inf
    if state['stick'] > 4:
        return inf
    if state['ingot'] > 6:
        return inf
    # need four more to craft bench
    if state['plank'] > 7:
        return inf
    if state['cobble'] > 8: 
        return inf
    return 0

def search(graph, state, is_goal, limit, heuristic):

    start_time = time()
    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state
    queue = [(0, state)]
    dist  = {}
    prev = {}
    actions = {}
    result = []
    dist[state] = 0
    prev[state] = None
    actions[state] = None
    explored_states = 0

    while queue and (time() - start_time < limit):
        priority,current_state = heappop(queue)
        if is_goal(current_state):
            while current_state:
                result.append((current_state, actions[current_state]))
                current_state = prev[current_state]
            result.reverse()
            print("states explored: ", explored_states)
            return result
        for action, next_state, cost in graph(current_state):
            explored_states += 1
            new_cost = priority + cost 
            if next_state not in dist or new_cost < dist[next_state]:
                dist[next_state] = new_cost
                prev[next_state] = current_state
                actions[next_state] = action
                heappush(queue, (new_cost + heuristic(next_state), next_state))
        #pass

    # Failed to find a path
    print(time() - start_time, 'seconds.')
    print("Failed to find a path from", state, 'within time limit.')
    return None

if __name__ == '__main__':
    start_time = time()
    with open('Crafting.json') as f:
        Crafting = json.load(f)

    # # List of items that can be in your inventory:
    print('All items:', Crafting['Items'])
    #
    # # List of items in your initial inventory with amounts:
    print('Initial inventory:', Crafting['Initial'])
    #
    # # List of items needed to be in your inventory at the end of the plan:
    print('Goal:',Crafting['Goal'])
    #
    # # Dict of crafting recipes (each is a dict):
    print('Example recipe:','craft stone_pickaxe at bench ->',Crafting['Recipes']['craft stone_pickaxe at bench'])

    # Build rules
    all_recipes = []
    for name, rule in Crafting['Recipes'].items():
        # print("name: ", name)
        # print("rule: ", rule)
        checker = make_checker(rule)
        effector = make_effector(rule)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)

    # Create a function which checks for the goal
    is_goal = make_goal_checker(Crafting['Goal'])

    # Initialize first state from initial inventory
    state = State({key: 0 for key in Crafting['Items']})
    state.update(Crafting['Initial'])

    # Search for a solution
    resulting_plan = search(graph, state, is_goal, 30, heuristic)
    cost = 0
    if resulting_plan:
        # Print resulting plan
        for state, action in resulting_plan:
            if action:
                cost += Crafting['Recipes'][action]['Time']
            print('\t', state)
            print(action)
        #minus one for the initial state
        print('cost =',cost,', len =' ,len(resulting_plan) - 1)
        print('Time elapsed: ', time() - start_time)
