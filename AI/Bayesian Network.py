# date: 04/11/16
# author: Guocheng Chen
# email: guochenc@usc.edu
# description: Bayesian Network

import sys
import getopt
import itertools

global INPUT_FILE_NAME
global OUTPUT_FILE_NAME


class BayesianNetwork(object):
    def __init__(self):
        self.query_list = []
        self.node_list = []
        self.decision_list = []
        self.node_name_list = []
        self.utility_node = None
        self.decision_map = {}
        self.var_values = ['+', '-']

    def __read_file(self):
        input_file = open(INPUT_FILE_NAME)
        content = input_file.readlines()
        content_len = len(content)
        line = 0
        while content[line].strip() != '******':
            self.query_list.append(content[line].strip())
            line += 1
        line += 1

        while line < content_len and content[line].strip() != '******':
            items = content[line].strip().split('|')
            node_name = items[0].strip()
            parents = []
            if len(items) == 2:
                parents = items[1].split()

            node = Node(node_name, parents)
            utility_flag = False
            if node_name == 'utility':
                utility_flag = True

            decision_flag = False
            line += 1
            while content[line].strip() != '***' and content[line].strip() != '******':
                if content[line].strip() == 'decision':
                    decision_flag = True
                    self.utility_node = node
                else:
                    tmp = content[line].strip().split()
                    probability = float(tmp[0])
                    combination = ''.join(tmp[1:])
                    if len(combination) == 0:
                        node.probability['+'] = probability
                        node.probability['-'] = 1 - probability
                    else:
                        node.probability[combination] = probability
                line += 1
                if line >= content_len:
                    break
            if utility_flag:
                self.utility_node = node
            if not utility_flag:
                self.node_list.append(node)
                self.node_name_list.append(node_name)
            if decision_flag:
                self.decision_list.append(node_name)

            line += 1

        input_file.close()

    def enumeration_ask(self, X, e):
        X_len = len(X)
        Q_x = {}
        p_sum = 0.0
        permutations = list(itertools.product(['+', '-'], repeat=X_len))

        for each_permutation in permutations:
            new_e = e.copy()
            for i in range(X_len):
                new_e[X[i]] = each_permutation[i]

            res = self.enumerate_all(self.node_name_list, new_e)
            p_sum += res
            Q_x[''.join(each_permutation)] = res

        for key in Q_x:
            Q_x[key] /= p_sum
        return Q_x

    def enumerate_all(self, vars, e):
        if len(vars) == 0:
            return 1.0
        y = vars[0]
        y_node = None
        for node in self.node_list:
            if node.node_name == y:
                y_node = node
                break
        if y in e:
            return y_node.get_probability(e[y], e) * self.enumerate_all(vars[1:], e)
        else:
            res = 0.0
            for y_i in self.var_values:
                res += y_node.get_probability(y_i, e) * self.enumerate_all(vars[1:], self.__extend(e, y, y_i))
            return res

    def __extend(self, evidence, y, value):
        new_evidence = evidence.copy()
        new_evidence[y] = value
        return new_evidence

    def run(self):
        self.__read_file()
        output_file = open(OUTPUT_FILE_NAME, 'w')

        for query in self.query_list:
            items = query.rstrip(')').split('(')
            qtype = items[0]
            terms = items[1].split('|')
            event = ''
            evidence = None
            #conditional
            if len(terms) == 2:
                event = terms[0]
                evidence = terms[1]
            elif len(terms) == 1:
                event = terms[0]

            query_states = event.split(',')

            query_list = []
            event_state = ''
            state_list = []
            meu_query_list = []
            meu_deleted_list = []
            for each_query in query_states:
                tmp = each_query.split('=')
                name = tmp[0].strip()
                if len(tmp) == 2:
                    event_state += (tmp[1].strip())
                    state_list.append(tmp[1].strip())
                    meu_deleted_list.append(name)
                elif len(tmp) == 1:
                    meu_query_list.append(name)
                query_list.append(name)

            evidence_map = {}
            if evidence:
                evidence_states = evidence.split(',')
                for each_evidence in evidence_states:
                    tmp = each_evidence.split('=')
                    evidence_map[tmp[0].strip()] = tmp[1].strip()

            if qtype == 'P':
                distribution = self.enumeration_ask(query_list, evidence_map)
                output_file.write('%.2f\n' % distribution[event_state])
                print round(distribution[event_state], 2)

            elif qtype == 'EU':

                utility = self.expected_utility(query_list, state_list, evidence_map)
                output_file.write('%.2f\n' % utility)
                print int(round(utility))
            elif qtype == 'MEU':
                meu_query_len = len(meu_query_list)

                meu = float('-Inf')
                state = []
                permutations = list(itertools.product(['+', '-'], repeat=meu_query_len))
                for each_permutation in permutations:
                    new_evidence_map = evidence_map.copy()
                    for idx in range(meu_query_len):
                        new_evidence_map[meu_query_list[idx]] = each_permutation[idx]

                    eu = self.expected_utility(meu_deleted_list, state_list, new_evidence_map)
                    if eu > meu:
                        state = each_permutation
                        meu = eu
                output_file.write('%d\n' % round(meu))
                print ' '.join(state), int(round(meu))

        #output_file = open(OUTPUT_FILE_NAME,'w')
        #output_file.close()

    def expected_utility(self, query_list, state_list, evidence_map):
        for idx in range(len(query_list)):
            evidence_map[query_list[idx]] = state_list[idx]

        eu_query_list = []
        for q in self.utility_node.parents:
            if q not in evidence_map:
                eu_query_list.append(q)
        distribution = self.enumeration_ask(eu_query_list, evidence_map)
        utility = 0.0

        for p in distribution:
            utility_state = list(p)
            parent_list = self.utility_node.parents
            for idx in range(len(parent_list)):
                if parent_list[idx] in evidence_map:
                    utility_state.insert(idx, evidence_map[parent_list[idx]])

            utility += distribution[p]*self.utility_node.probability[''.join(utility_state)]

        return utility


class Node(object):
    def __init__(self, node_name, parents):
        self.node_name = node_name
        self.parents = parents
        self.probability = {}

    def get_probability(self, query_state, evidence):
        if len(self.probability) == 0:
            return 1.0
        if query_state == '+':
            if len(self.parents) == 0:
                return self.probability['+']
            else:
                return self.probability[self.__join_evidence(evidence, self.parents)]
        elif query_state == '-':
            if len(self.parents) == 0:
                return self.probability['-']
            else:
                return 1 - self.probability[self.__join_evidence(evidence, self.parents)]

    def __join_evidence(self, evidence, parent):
        return ''.join(evidence[var] for var in parent)

if __name__ == '__main__':
    opts, args_in = getopt.getopt(sys.argv[1:], '-i:')
    for op, arg in opts:
        if op == '-i':
            INPUT_FILE_NAME = arg
            OUTPUT_FILE_NAME = '.output.'.join(arg.split('.'))
            #OUTPUT_FILE_NAME = 'test.txt'
        else:
            sys.exit()

    agent = BayesianNetwork()
    agent.run()
