# date: 02/06/16
# modify date 02/16/16
# author: Guocheng Chen
# email: guochenc@usc.edu
# email2: kwokshingchan92@gmail.com
# description: a game search program

import sys
import copy
import getopt

BOARD_SIZE = 5
BOARD_VALUE = []
RAID = 1
SNEAK = -1
DIRECTION = [-1,0,0,1,1,0,0,-1]

class Greedy_BFS(object):
    def __init__(self, type, **args): 
        self.max_val = 0
        if type == 'first':
            self.player = args['player']
            self.enemy = args['player_2']
            self.cutting_off_depth = args['depth']
        elif type == 'second':
            self.player = args['player_2']
            self.enemy = args['player']
            self.cutting_off_depth = args['depth_2']
        self.left_step = args['left_step']
        self.next_state_file_name = args['next_state_file']
        self.next_state = []
        self.current_state = copy.deepcopy(args['current_state'])
    
    def check_intersect(self, current_state, row, col, player, enemy):
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE: 
            if current_state[row][col] == enemy:
                return 1
            elif current_state[row][col] == player:
                return -1
            else:
                return 0
        else:
            #out of range
            return 0
    
#    def calculate_val(self, row, col):
#        action = SNEAK 
#        cur_val = BOARD_VALUE[row][col]
#        occupied_val = 0
#        conquered_list = []
#        for i in range(0,7,2):
#            row_offset = row+DIRECTION[i]
#            col_offset = col+DIRECTION[i+1]
#            ret_val = self.check_intersect(self.current_state, row_offset, col_offset, self.player, self.enemy)
#            #enemy around
#            if ret_val == 1:
#                occupied_val += BOARD_VALUE[row_offset][col_offset]
#                conquered_list.append(i)
#            #self around
#            elif ret_val == -1:
#                action = RAID
#        next_state_try = copy.deepcopy(self.current_state) 
#        next_state_try[row][col] = self.player 
#        #Raid, update the conquered nodes
#        if action == SNEAK:
#            return cur_val, next_state_try
#        elif action == RAID:
#            for i in conquered_list:
#                next_state_try[row+DIRECTION[i]][col+DIRECTION[i+1]] = self.player
#            return cur_val + occupied_val, next_state_try
    
#    def run(self):
#        for row in range(BOARD_SIZE):
#            for col in range(BOARD_SIZE):
#                if self.current_state[row][col] == '*':
#                    cur_val, next_state_try = self.calculate_val(row, col)
#                    if cur_val > self.max_val:
#                        self.next_state = next_state_try
#                        self.max_val = cur_val
#                else:
#                    pass
#        self.output_next_state(self.next_state_file_name) 
#        return self.next_state

    def output_next_state(self,output_file_name):
        output_file = open(output_file_name,'w')
        for item in self.next_state:
            output_file.write(''.join(item) + '\n')
        output_file.close()

class Minimax(Greedy_BFS):
    def __init__(self, type, **args): 
        super(Minimax,self).__init__(type, **args)
        self.traverse_file = open(args['traverse_log_file'],'w')

    def run(self, depth = 0):
        root_val = -float('inf')
        self.traverse_file.write('Node,Depth,Value\n')
        score = self.maxi(depth, self.left_step, self.current_state, 'root')
        self.traverse_file.close()
        
        self.output_next_state(self.next_state_file_name)
        return self.next_state

    def maxi(self, depth, step_number, pre_state, parent):
        if depth == self.cutting_off_depth or terminate(step_number):
            score = self.utility(pre_state)
            self.traverse_file.write('%s,%d,%s\n' % (parent,depth,self.num2str(score)))
            return score
        max_val = -float('inf')
        score = -float('inf')
        self.traverse_file.write('%s,%d,%s\n' % (parent,depth,self.num2str(max_val)))
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if pre_state[row][col] == '*':
                    position = chr(col+65)+str(row+1)
                    next_state_try = self.child_action(row, col, pre_state, self.player, self.enemy)
                    
                    score = self.mini(depth+1, step_number-1, next_state_try, position)
                    if score > max_val:
                        max_val = score
                        if depth == 0:
                            self.next_state = next_state_try
                    self.traverse_file.write('%s,%d,%s\n' % (parent,depth,self.num2str(max_val)))
        return max_val

    def mini(self, depth, step_number, pre_state, parent):
        if depth == self.cutting_off_depth or terminate(step_number):
            score = self.utility(pre_state)
            self.traverse_file.write('%s,%d,%s\n' % (parent,depth,self.num2str(score))) 
            return score 
        min_val = float('inf')
        score = float('inf')
        self.traverse_file.write('%s,%d,%s\n' % (parent,depth,self.num2str(min_val))) 
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if pre_state[row][col] == '*':
                    position = chr(col+65)+str(row+1)
                    next_state_try = self.child_action(row, col, pre_state, self.enemy, self.player)
                        
                    score = self.maxi(depth+1, step_number-1, next_state_try, position)
                    if score < min_val:
                        min_val = score
                    self.traverse_file.write('%s,%d,%s\n' % (parent,depth,self.num2str(min_val))) 
        return min_val

    def child_action(self, row, col, pre_state, player, enemy):
        conquered_list = []
        action = SNEAK
        for i in range(0,7,2):
            row_offset = row+DIRECTION[i]
            col_offset = col+DIRECTION[i+1]
            ret_val = self.check_intersect(pre_state, row_offset, col_offset, player, enemy)
            #enemy around
            if ret_val == 1:
                conquered_list.append(i)
            #self around
            elif ret_val == -1:
                action = RAID
        next_state_try = copy.deepcopy(pre_state) 
        next_state_try[row][col] = player
        if action == RAID:
            for i in conquered_list:
                next_state_try[row+DIRECTION[i]][col+DIRECTION[i+1]] = player
        return next_state_try

    def utility(self, current_state):
        player_value = 0
        enemy_value = 0
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if current_state[row][col] == '*':
                    continue
                if current_state[row][col] == self.player:
                    player_value += BOARD_VALUE[row][col]
                elif current_state[row][col] == self.enemy:
                    enemy_value += BOARD_VALUE[row][col]
        return player_value - enemy_value
        
    def num2str(self, number):
        if number == float('inf'):
            return 'Infinity'
        elif number == -float('inf'):
            return '-Infinity'
        else:
            return str(number)
    

class Alpha_Beta_Pruning(Minimax):
    def __init__(self, type, **args): 
        super(Alpha_Beta_Pruning, self).__init__(type, **args)
        self.traverse_file = open(args['traverse_log_file'],'w')
        self.alpha = -float('inf')
        self.beta = float('inf')

    def run(self, depth = 0):
        root_val = -float('inf')
        alpha = -float('inf')
        beta = float('inf')
        self.traverse_file.write('Node,Depth,Value,Alpha,Beta\n')
        score = self.max_step(depth, self.current_state, 'root', alpha, beta, self.left_step)
        self.traverse_file.close()
        
        self.output_next_state(self.next_state_file_name)
        return self.next_state

    def max_step(self, depth, pre_state, parent, alpha, beta, left_step):
        if depth == self.cutting_off_depth or terminate(left_step):
            score = self.utility(pre_state)
            self.traverse_file.write('%s,%s,%s,%s,%s\n' % (parent,depth,self.num2str(score),self.num2str(alpha),self.num2str(beta)))
            return score
        score = -float('inf')
        max_score = -float('inf')
        self.traverse_file.write('%s,%s,%s,%s,%s\n' % (parent,depth,self.num2str(score),self.num2str(alpha),self.num2str(beta)))
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if pre_state[row][col] == '*':
                    position = chr(col+65)+str(row+1)
                    next_state_try = self.child_action(row, col, pre_state, self.player, self.enemy)
                    
                    score = max(score, self.min_step(depth+1, next_state_try, position, alpha, beta, left_step-1))
                    if depth == 0 and max_score < score:
                        max_score = score
                        self.next_state = next_state_try
                    if score >= beta:
                        self.traverse_file.write('%s,%s,%s,%s,%s\n' % (parent,depth,self.num2str(score),self.num2str(alpha),self.num2str(beta)))
                        return score
                    alpha = max(alpha, score)
                    self.traverse_file.write('%s,%s,%s,%s,%s\n' % (parent,depth,self.num2str(score),self.num2str(alpha),self.num2str(beta)))
        self.alpha = alpha
        self.beta = beta
        return score

    def min_step(self, depth, pre_state, parent, alpha, beta, left_step):
        if depth == self.cutting_off_depth or terminate(left_step):
            score = self.utility(pre_state)
            self.traverse_file.write('%s,%s,%s,%s,%s\n' % (parent,depth,self.num2str(score),self.num2str(alpha),self.num2str(beta)))
            return score 
        score = float('inf')
        self.traverse_file.write('%s,%s,%s,%s,%s\n' % (parent,depth,self.num2str(score),self.num2str(alpha),self.num2str(beta)))
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if pre_state[row][col] == '*':
                    position = chr(col+65)+str(row+1)
                    next_state_try = self.child_action(row, col, pre_state, self.enemy, self.player)
                    
                    score = min(score, self.max_step(depth+1, next_state_try, position, alpha, beta, left_step-1))
                    if score <= alpha:
                        self.traverse_file.write('%s,%s,%s,%s,%s\n' % (parent,depth,self.num2str(score),self.num2str(alpha),self.num2str(beta)))
                        return score
                    beta = min(beta, score)
                    self.traverse_file.write('%s,%s,%s,%s,%s\n' % (parent,depth,self.num2str(score),self.num2str(alpha),self.num2str(beta)))
        return score

class Battle(object):
    pass


def terminate(step_number):
    if step_number == 0:
        return True
    return False

def init_state(input_file_name):
    global BOARD_VALUE
    
    args = {}
    input_file = open(input_file_name)
    lines = input_file.readlines()
    args['task'] = lines[0].strip()

    content_size = len(lines)
    for i in range(content_size-10, content_size-5):
        tmp_list = []
        for num in lines[i].strip().split():
            tmp_list.append(int(num))
        BOARD_VALUE.append(tmp_list)
    args['current_state'] = [list(lines[i].strip()) for i in range(content_size-5, content_size)]
    args['left_step'] = sum([lines[i].strip().count('*') for i in range(content_size-5, content_size)])
    if args['task'] != '4':
        args['agent_num'] = int(lines[0].strip())
        args['player'] = lines[1].strip()
        args['depth'] = int(lines[2].strip())
        args['player_2'] = 'X' if args['player'] =='O' else 'O' 
        args['agent_num_2'] = 0
        args['depth_2'] = 0
    else:
        args['player'] = lines[1].strip()
        args['agent_num'] = int(lines[2].strip())
        args['depth'] = int(lines[3].strip())
        args['player_2'] = lines[4].strip()
        args['agent_num_2'] = int(lines[5].strip())
        args['depth_2'] = int(lines[6].strip())
    
    args['next_state_file'] = 'next_state.txt'
    args['traverse_log_file'] = 'traverse_log.txt'
    input_file.close()
    return args

if __name__ =='__main__':
    opts, args_in = getopt.getopt(sys.argv[1:], '-i:')
    input_file_name = ''
    output_file_name = 'test.next_state.txt'
    for op, arg in opts:
        if op == '-i':
            input_file_name = arg
        else:
            sys.exit()
    args = init_state(input_file_name)
    
    task = args['task']
    agent_num = args['agent_num']
    agent_num_2 = args['agent_num_2']
    if task == '1':
        #agent = Greedy_BFS('first', **args)
        agent = Minimax('first', **args)
        next_state = agent.run()
    elif task == '2':
        agent = Minimax('first', **args)
        next_state = agent.run()
    elif task == '3':
        agent = Alpha_Beta_Pruning('first', **args)
        next_state = agent.run()
    elif task == '4':
        enemy_state = []
        test_output = open('trace_state.txt','w')
        player_agent = None
        enemy_agent = None
        next_state = []
        enemy_state = []
        if agent_num == 1:
            #Greedy_BFS uses the wrong utility function, leading to a bug
            #Simply change it to Minimax with depth = 1
            #player_agent = Greedy_BFS('first', **args)
            player_agent = Minimax('first', **args)
        elif agent_num == 2:
            player_agent = Minimax('first', **args)
        elif agent_num == 3:
            player_agent = Alpha_Beta_Pruning('first', **args)

        next_state = player_agent.run()
        for item in next_state:
            test_output.write(''.join(item)+'\n')
            print ''.join(item)
        args['left_step'] -= 1
        if terminate(args['left_step']):
            test_output.close()
            exit()
        args['current_state'] = next_state
        if agent_num_2 == 1:
            #enemy_agent = Greedy_BFS('second', **args)
            enemy_agent = Minimax('second', **args)
        elif agent_num_2 == 2:
            enemy_agent = Minimax('second', **args)
        elif agent_num_2 == 3:
            enemy_agent = Alpha_Beta_Pruning('second', **args)
        
        enemy_state = enemy_agent.run()
        for item in enemy_state:
            test_output.write(''.join(item)+'\n')
            print ''.join(item)

        args['left_step'] -= 1
        
        while True:
            if terminate(args['left_step']):
                break
            args['current_state'] = enemy_state
            player_agent.__init__('first', **args)
            next_state = player_agent.run()
            for item in next_state:
                test_output.write(''.join(item)+'\n')
                print ''.join(item)
            args['left_step'] -= 1
            if terminate(args['left_step']):
                break
            args['current_state'] = next_state
            enemy_agent.__init__('second', **args)
            enemy_state = enemy_agent.run()
            for item in enemy_state:
                test_output.write(''.join(item)+'\n')
                print ''.join(item)
            args['left_step'] -= 1
        
        test_output.close()
