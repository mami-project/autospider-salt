#!/usr/bin/env python2

import sys
import json
import random

import salt.cloud

def readout_config(path):
    config_file = open(path)
    config = json.loads(config_file.read())
    config_file.close()
    
    return config

class Minion():
    NAME_TEMPLATE = '{web}-{profile}-{index}'

    def __init__(self, name, profile, grains=None):
        self.name = name
        self.profile = profile
        if grains:
            self.grains = grains
        else:
            grains = {}
   
    def __repr__(self):
        string = "<Worker: {}>".format(self.name)
        return string

    def get_name(self):
        return self.name

    def get_profile(self):
        return profile

    def get_config(self):
        return {'grains': self.grains}

class Profile():
    def __init__(self, name):
        self.name = name
        self.counter = 0
        self.minions = set()

    def __iter__(self):
        return self.minions.__iter__()

    def get_name(self):
        return self.name

    def add_minion(self, web , grains=None ,count=1):
        for i in range(count):
            name = Minion.NAME_TEMPLATE.format(
                    web = web.get_name(),
                    profile = self.name,
                    index = self.counter)
            self.counter = self.counter + 1
            self.minions.add(Minion(name, self, grains))

class Web():
    WEB_NAME_CHARS = \
        '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    WEB_NAME_LENGTH = 10

    def __init__(self, config_file):
        self.profiles = set()
        self.generate_name()
        self.readout_config(config_file)

    def __iter__(self):
        return self.profiles.__iter__()

    def generate_name(self):
        name = ''
        for i in range(self.WEB_NAME_LENGTH):
            name += random.choice(self.WEB_NAME_CHARS)
        self.name = name
        
        return name

    def get_name(self):
        return self.name

    def readout_config(self, path):
        config_file = open(path)
        self.config = json.loads(config_file.read())
        config_file.close()

        self.verify_config()
        
        self.read_grains_from_config()
        self.add_minions_from_config()

        return self.config

    def verify_config(self):
        pass

    def read_grains_from_config(self):
        grains = {}
        grains['pathspider_flags'] = self.config['pathspider_flags']
        grains['when_done'] = self.config['when_done']
        grains['campaign'] = self.config['campaign']
        self.grains = grains

    def add_minions_from_config(self):
        for profile in self.config['minions']:
            new_profile = Profile(profile)
            new_profile.add_minion(web = self,
                count = self.config['minions'][profile],
                grains = self.grains)
            self.profiles.add(new_profile)
   
    def spawn(self):
        client = salt.cloud.CloudClient(path='/etc/salt/cloud')
        for profile in self:
            for minion in profile:
                client.profile(profile.get_name(), names=[minion.get_name(),],
                    minion=minion.get_config())

w = Web(sys.argv[1])

for profile in w:
    for minion in profile:
        print(minion)

print(w.spawn())
