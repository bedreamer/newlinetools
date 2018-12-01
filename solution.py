# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import codecs
import json
import time


class SolutionStep(object):
    def __init__(self, name, idx, **kwargs):
        self.name = name
        self.idx = idx
        self.loop = 0
        self.born = 0

        for key, value in kwargs.items():
            setattr(self, key, value)

    def weapons_on(self):
        self.loop += 1
        self.born = time.time()
        print("weapons on", self.name)
        return self

    def __str__(self):
        return ''.join([self.name, '@', str(self.idx)])

    def true_step(self, steps):
        next_step_name = getattr(self, 'true')
        if next_step_name == '$auto':
            return steps[self.idx + 1]
        else:
            for step in steps:
                if step.name == next_step_name:
                    return step

            raise ValueError("step %s not found" % next_step_name)

    def false_step(self, steps):
        next_step_name = getattr(self, 'false')
        if next_step_name == '$auto':
            next_step_name = self.name

        for step in steps:
            if step.name == next_step_name:
                return step

        raise ValueError("step %s not found" % next_step_name)

    def is_timeout(self):
        ttl = getattr(self, 'ttl')
        if ttl < 0:
            return False

        return False if time.time() - self.born < ttl else True

    def is_satisfy(self, bms, newline):
        tiaojian = getattr(self, 'tiaojian')
        return eval(" ".join(tiaojian))


class EndStep(SolutionStep):
    def __init__(self, idx):
        super().__init__('$end', idx)

    def weapons_on(self):
        print("steps executed done.")
        return self

    def true_step(self, steps):
        return None

    def false_step(self, steps):
        return None

    def is_timeout(self):
        return False

    def is_satisfy(self, bms, newline):
        return False


class Solution:
    def __init__(self, bms, newline, control_solution_file_name):
        self.bms = bms
        self.newline = newline
        self.control_solution_file_name = control_solution_file_name
        self.name, self.main, self.steps = None, None, None

        self.run_cmommand = 'stop'
        self.ui_wsapi = dict()

    def register_ui(self, path, wsapi):
        print("+ register", path, wsapi)
        try:
            self.ui_wsapi[path].append(wsapi)
        except Exception as e:
            self.ui_wsapi[path] = list([wsapi])

    def unregister_ui(self, path, wsapi):
        print("- unregister", path, wsapi)
        try:
            self.ui_wsapi[path].remove(wsapi)
        except Exception as e:
            pass

    def push_step_changed(self, old_step, new_step):
        try:
            wsapi_list = self.ui_wsapi['/newline/']
        except KeyError:
            wsapi_list = list()

        for wsapi in wsapi_list:
            wsapi.push_step_changed(vars(old_step), vars(new_step))

    @classmethod
    def load_from_file(cls, steps_full_path):
        with codecs.open(steps_full_path) as file:
            steps = json.load(file)

        steps_list = list()
        idx = 0
        for name, step_dict in steps['steps'].items():
            step = SolutionStep(name, idx, **step_dict)
            steps_list.append(step)
            idx += 1

        end_step = EndStep(idx)
        steps_list.append(end_step)

        main_step = None
        for step in steps_list:
            if step.name == steps['main']:
                main_step = step

        if main_step is None:
            raise ValueError("main step:%s invalid." % steps['main'])

        return steps['name'], main_step, steps_list

    def run_step_forward(self):
        if self.run_cmommand == 'stop':
            return

        if self.run_cmommand == 'pause':
            return

        bms = self.bms.pack_all()
        newline = self.newline.pack_all()
        step = self.main

        timeout, satisfy = step.is_timeout(), step.is_satisfy(bms, newline)
        if True in [timeout, satisfy]:
            # 工步因超时结束
            step = step.true_step(self.steps)
        else:
            step = step.false_step(self.steps)

        if step is None:
            return False

        if step != self.main:
            self.push_step_changed(self.main, step)
            self.main = step.weapons_on()

        return True

    def get_solution_steps_as_json(self, name=None):
        with codecs.open(self.control_solution_file_name) as file:
            steps = json.load(file)

        if name is None:
            return steps
        elif name in steps['steps']:
            return {"name": name, "data": steps['steps'][name]}
        else:
            return None

    def save_solution_single_step(self, name, step):
        with codecs.open(self.control_solution_file_name) as file:
            steps = json.load(file)

        steps['steps'][name] = step
        with codecs.open(self.control_solution_file_name, 'w') as file:
            json.dump(steps, file, indent=2, ensure_ascii=False)

        return steps

    def steps_start(self, entry=None):
        self.name, self.main, self.steps = self.load_from_file(self.control_solution_file_name)
        self.main.weapons_on()

    def steps_stop(self):
        self.run_cmommand = 'stop'

    def steps_pause(self):
        self.run_cmommand = 'pause'

    def steps_reboot(self, entry):
        pass

    def steps_status(self):
        pass

    def steps_check(self):
        pass
