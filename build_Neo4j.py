#!/usr/bin/env python3
# coding: utf-8
# File: MilitaryGraph.py
# Author: heliu
# Date: 19-8-30

import os
import re
import csv
import json
from py2neo import Graph, Node


def read_data():
    handler.read_component()
    # handler.read_weapon()
    # handler.read_fault()
    # handler.read_system()
    return


def transfer(attr):
    ratio = 1
    if 'M' in attr:
        ratio = 1000000
    elif 'k' in attr or 'K' in attr:
        ratio = 1000
    elif 'm' in attr:
        ratio = 0.001

    return ratio


class MilitaryGraph:

    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        self.data_path_component = os.path.join(cur_dir, 'data/yuanqijian_try.csv')

        self.data_path_weapon = os.path.join(cur_dir, 'data/military_air_noChina_demo.json')
        self.data_path_fault = os.path.join(cur_dir, 'data/fault.csv')
        self.data_path_rel = os.path.join(cur_dir, 'data/kzhou.csv')

        self.g = Graph(
            host="127.0.0.1",  # neo4j 搭载服务器的ip地址，ifconfig可获取到
            http_port=7474,  # neo4j 服务器监听的端口号
            user="neo4j",  # 数据库user name，如果没有更改过，应该是neo4j
            password="!@aA123456")

        # 实体
        # 元器件级实体
        self.components_entity = []  # 元器件 almost unuseful
        self.components_infos = []  # 元器件实体信息
        self.components_cats = []  # 元器件分类
        self.components_city = []  # 元器件生产城市
        self.components_cats_i = []  # 元器件分类
        self.components_city_i = []  # 元器件生产城市
        self.components_organizations = []  # 元器件生产厂家
        self.components_quality = []
        self.components_name = []
        self.components_encap_mode = []
        # 元器件关系
        self.rels_component_city = []  # 元器件-生产城市从属关系
        self.rels_component_organization = []  # 元器件-产商从属关系
        self.rels_component_comCats = []  # 元器件-类型从属关系
        self.provinces = ['北京', '天津', '上海', '重庆', '河北', '山西', '辽宁', '吉林', '黑龙江', '江苏', '浙江', '安徽',
                         '福建', '江西', '山东', '河南', '湖北', '湖南', '广东', '海南', '四川', '贵州', '云南', '陕西',
                         '甘肃', '青海', '台湾', '内蒙古', '广西', '西藏', '宁夏', '新疆', '香港', '澳门']
        # 武器实体
        self.weapons_cats = []  # 武器大类
        self.weapons_types = []  # 武器类型
        self.weapons_entity = []  # 武器实体
        self.weapon_infos = []  # 武器实体信息
        self.weapons_country = []  # 武器产国
        self.weapons_organizations = []  # 武器产商
        # 武器关系
        self.rels_weapon_country = []  # 武器-产国从属关系
        self.rels_weapon_organization = []  # 武器-研发机构从属关系
        self.rels_weapon_type = []  # 武器－类型的关系
        self.rels_type_weaCats = []  # 武器类型-大类的关系

        # 系统级实体
        self.systems_entity = []  # 系统实体
        self.systems_infos = []  # 系统实体信息
        # 部件级实体
        self.units_entity = []  # 部件实体
        self.units_infos = []  # 部件实体信息
        # 故障实体
        self.malfunctions_entity = []  # 部件级故障
        self.malfunctions_infos = []  # 故障实体信息

        # 其他实体
        self.weapon_chargers = []  # 武器主管单位
        self.weapon_users = []  # 武器使用方
        self.weapon_useEnvs = []  # 武器使用环境
        self.charger_actions = []  # 主管单位处理措施
        self.unit_orgs = []  # 部件生产厂
        self.test_orgs = []  # 试验厂所
        self.test_names = []  # 试验项
        self.test_types = []  # 试验类型
        self.fault_causes = []  # 故障原因
        # 其他关系
        self.rels_comCats_malfunction = []  # 元器件类-故障的关系
        self.rels_unit_fault = []  # 部件-故障关系
        self.rels_system_unit = []  # 部件-系统关系
        self.rels_unit_comCats = []  # 部件-元器件类关系
        self.rels_weapon_system = []  # 武器-系统
        self.rels_weaponOrg_unitOrg = []  # 主机厂-部件厂
        self.rels_unitOrg_componentOrg = []  # 部件厂-元器件厂
        self.rels_componentOrg_component = []  # 元器件厂-元器件
        self.rels_weapon_charger = []  # 武器-主管单位
        self.rels_charger_action = []  # 主管单位-处理措施
        self.rels_weapon_fault = []  # 武器-武器级故障
        self.rels_unit_testType = []  # 部件-试验类型
        self.rels_testType_testOrg = []  # 试验类型-试验厂所
        self.rels_testOrg_testName = []  # 试验厂所-试验项
        self.rels_testName_componentFault = []  # 试验项-故障元器件
        self.rels_weapon_user = []  # 武器-使用方
        self.rels_user_useEnv = []  # 使用方-使用环境
        self.rels_useEnv_componentFault = []  # 使用环境-故障元器件
        self.rels_componentFault_faultcause = []  # 元器件故障-故障原因
        self.rels_faultcause_user = []  # 故障原因-发现方

    '''读取jason文件中的武器数据，建立武器级节点与关系'''
    def read_weapon(self):
        for data in open(self.data_path_weapon, encoding='UTF-8'):
            weapon_dict = {}
            data_json = json.loads(data)
            weapon = data_json['名称']
            self.weapons_entity.append(weapon)

            weapon_dict['name'] = weapon
            weapon_dict['flightV'] = ''
            weapon_dict['length'] = ''
            weapon_dict['weapons'] = ''
            weapon_dict['max_V'] = ''
            weapon_dict['max_L'] = ''
            weapon_dict['wing'] = ''
            weapon_dict['desc'] = ''
            if '飞行速度' in data_json:
                weapon_dict['flightV'] = data_json['飞行速度']
            if '机长' in data_json:
                weapon_dict['length'] = data_json['机长']
            if '最大飞行速度' in data_json:
                weapon_dict['max_V'] = data_json['最大飞行速度']
            if '最大航程' in data_json:
                weapon_dict['max_L'] = data_json['最大航程']
            if '翼展' in data_json:
                weapon_dict['wing'] = data_json['翼展']
            if '简介' in data_json:
                weapon_dict['desc'] = data_json['简介']
            # if '首飞时间' in data_json:
            #     weapon_dict['first_fly'] = data_json['首飞时间']
            # if '建造时间' in data_json:
            #     weapon_dict['first_fly'] = data_json['首飞时间']
            # if '诞生时间' in data_json:
            #     weapon_dict['first_fly'] = data_json['首飞时间']
            self.weapon_infos.append(weapon_dict)

            if '产国' in data_json:
                made_site = data_json['产国']
                self.weapons_country += [made_site]
                self.rels_weapon_country.append([weapon, made_site])

            if '研发单位' in data_json:
                made_org = data_json['研发单位']
                self.weapons_organizations += [made_org]
                self.rels_weapon_organization.append([weapon, made_org])

            if '制造厂' in data_json:
                made_org = data_json['制造厂']
                self.weapons_organizations += [made_org]
                self.rels_weapon_organization.append([weapon, made_org])

            if '制造商' in data_json:
                made_org = data_json['制造商']
                self.weapons_organizations += [made_org]
                self.rels_weapon_organization.append([weapon, made_org])

            if '大类' in data_json:
                weapon_cat = data_json['大类']
                self.weapons_cats += [weapon_cat]

            if '类型' in data_json:
                weapon_type = data_json['类型']
                self.weapons_types += [weapon_type]
                self.rels_weapon_type.append([weapon, weapon_type])

            if '大类' in data_json and '类型' in data_json:
                tmp_cat = data_json['大类']
                tmp_type = data_json['类型']
                self.rels_type_weaCats.append([tmp_type, tmp_cat])

    def read_component(self):
        with open(self.data_path_component, 'r', encoding="utf-8") as csvfile:
            lines = csv.reader(csvfile, delimiter=',')
            for line in lines:
                component_type = line[3]
                self.components_entity.append(component_type)  # used for export and debug so
                self.components_name.append(line[1])
                components_dict = {
                    'type': component_type,  # 型号 str
                    'name': line[1],  # 名称 str
                    # 'quality': '', # 质量等级 str
                    # 'encap_mode': '', # 封装形式 str
                    # 'desc': '', # 产品特点及用途 str
                    # 'colorLevel': '', # FIXME:这个是干嘛用的 str
                    # 'tmp_char': 0.0, #  温度特性: 单位+- ppm/℃ float FIXME: can it work??? 注意到有些项为空，能不能不要
                    # 'tmp_lower': 0.0, # 温度范围下界 float 单位 ℃
                    # 'tmp_upper': 0.0, # 温度范围上界 float 单位 ℃
                    # 'res_lower': 0.0, # 阻值范围下界 float 单位 Ω
                    # 'res_upper': 0.0, # 阻值范围上界 float 单位 Ω
                    # 'power': 0.0, # 额定功耗 float 单位 W
                    # 'weight': 0.0, # 重量 float 单位 g
                    # 'size': 0.0, # 封装尺寸 float 单位？ FIXME: 这个要如何计算，先用一个临时的计算方案替代了
                }
                if '质量等级' in line:
                    quality = line[line.index('质量等级') + 1]
                    components_dict['quality'] = quality
                    self.components_quality.append(quality)
                if '封装形式' in line:
                    encap_mode = line[line.index('封装形式') + 1]
                    components_dict['encap_mode'] = encap_mode
                    self.components_encap_mode.append(encap_mode)
                if '产品特点及用途' in line:
                    components_dict['desc'] = line[line.index('产品特点及用途') + 1]

                # 下面开始python的脚本数据处理
                if '温度特性' in line:
                    numbers = list(map(float, re.findall(r'[-+]?\d*\.\d+|[-+]?\d+', line[line.index('温度特性') + 1])))
                    components_dict['tmp_char'] = numbers[0]
                if '温度范围' in line:
                    numbers = list(map(float, re.findall(r'[-+]?\d*\.\d+|[-+]?\d+', line[line.index('温度范围') + 1])))
                    components_dict['tmp_lower'] = numbers[0]  # left most
                    components_dict['tmp_upper'] = numbers[-1]  # right most
                if '阻值范围' in line:  # 注意单位换算
                    attr = line[line.index('阻值范围') + 1]
                    ratio = transfer(attr)
                    numbers = list(map(float, re.findall(r'[-+]?\d*\.\d+|[-+]?\d+', attr)))
                    numbers = [n * ratio for n in numbers]
                    components_dict['res_lower'] = numbers[0]  # left most
                    components_dict['res_upper'] = numbers[-1]  # right most
                if '标称阻值' in line:
                    attr = line[line.index('标称阻值') + 1]
                    ratio = transfer(attr)
                    numbers = list(map(float, re.findall(r'[-+]?\d*\.\d+|[-+]?\d+', attr)))
                    components_dict['res_lower'] = ratio * numbers[0]
                    components_dict['res_upper'] = ratio * numbers[0]
                if '最大阻值' in line:
                    attr = line[line.index('最大阻值') + 1]
                    ratio = transfer(attr)
                    numbers = list(map(float, re.findall(r'[-+]?\d*\.\d+|[-+]?\d+', attr)))
                    components_dict['res_lower'] = ratio * numbers[0]
                    components_dict['res_upper'] = ratio * numbers[0]
                if '额定功耗' in line:
                    attr = line[line.index('额定功耗') + 1]
                    ratio = transfer(attr)
                    numbers = list(map(float, re.findall(r'[-+]?\d*\.\d+|[-+]?\d+', attr)))
                    components_dict['power'] = ratio * numbers[0]
                if '重量' in line:  # 注意单位换算
                    attr = line[line.index('重量') + 1]
                    ratio = transfer(attr)
                    numbers = list(map(float, re.findall(r'[-+]?\d*\.\d+|[-+]?\d+', attr)))
                    components_dict['weight'] = ratio * numbers[0]
                if '封装尺寸' in line:
                    # FIXME!!!
                    numbers = list(map(float, re.findall(r'[-+]?\d*\.\d+|[-+]?\d+', line[line.index('封装尺寸') + 1])))
                    if len(numbers) > 0:
                        components_dict['size'] = numbers[0]

                self.components_infos.append(components_dict)

                # 添加分类信息
                if '分类' in line:
                    component_cat = line[5]
                    if component_cat not in self.components_cats:
                        category = {'name': component_cat}
                        if '电阻' in component_cat:
                            category['type'] = '电阻'
                        if '振荡器' in component_cat:
                            category['type'] = '振荡器'
                        self.components_cats_i.append(category)
                        self.components_cats.append(component_cat)

                    self.rels_component_comCats.append([component_type, component_cat])

                if '生产厂家' in line:
                    component_organizations = line[7]
                    self.components_organizations.append(component_organizations)
                    self.rels_component_organization.append([component_type, component_organizations])

                if '厂商地域' in line:
                    component_city = line[9]
                    if component_city not in self.components_city:
                        city = {'name': component_city, 'China': False}
                        for province in self.provinces:
                            if province in component_city:
                                city['China'] = True
                                break
                        self.components_city_i.append(city)
                        self.components_city.append(component_city)

                    self.rels_component_city.append([component_type, component_city])

            self.components_organizations = list(set(self.components_organizations))
            self.components_entity = list(set(self.components_entity))
            # self.components_cats = list(set(self.components_cats))
            # self.components_city = list(set(self.components_city))

            self.components_name = list(set(self.components_name))
            self.components_quality = list(set(self.components_quality))
            self.components_encap_mode = list(set(self.components_encap_mode))

    def read_fault(self):
        with open(self.data_path_fault, 'r', encoding="utf-8") as csvfile:
            lines = csv.reader(csvfile, delimiter=',')
            for line in lines:
                # fault_dict = {}
                fault_unit_name = line[1]
                self.units_entity += [fault_unit_name]
                # fault_dict['name'] = fault_unit_name
                # components_id.append(component_ID)

                if '故障件所属系统' in line:
                    system_name = line[line.index('故障件所属系统') + 1]
                    self.systems_entity += [system_name]
                    self.rels_system_unit.append([system_name, fault_unit_name])

                if '故障件所属武器' in line and '故障件所属系统' in line:
                    weapon_name = line[line.index('故障件所属武器') + 1]
                    system_name = line[line.index('故障件所属系统') + 1]
                    self.rels_weapon_system.append([weapon_name, system_name])

                if '设备故障模式' in line:
                    fault_unit = line[line.index('设备故障模式') + 1]
                    self.malfunctions_entity += [fault_unit]
                    self.rels_unit_fault.append([fault_unit_name, fault_unit])

                if '元器件故障' in line and '故障元器件' in line:
                    fault_component = line[line.index('元器件故障') + 1]
                    com_cats = line[line.index('故障元器件') + 1]
                    self.malfunctions_entity += [fault_component]
                    self.rels_comCats_malfunction.append([com_cats, fault_component])
                if '故障元器件' in line:
                    com_cats = line[line.index('故障元器件') + 1]
                    self.rels_unit_comCats.append([fault_unit_name, com_cats])

    def read_system(self):
        with open(self.data_path_rel, 'r', encoding="utf-8") as csvfile:
            lines = csv.reader(csvfile, delimiter=',')
            for line in lines:
                if '部件厂' in line and '主机厂' in line:
                    unit_org = line[line.index('部件厂') + 1]
                    weapon_org = line[line.index('主机厂') + 1]
                    self.unit_orgs += [unit_org]  # 部件生产厂
                    self.rels_weaponOrg_unitOrg.append([weapon_org, unit_org])

                if '部件厂' in line and '元器件厂' in line:
                    unit_org = line[line.index('部件厂') + 1]
                    component_org = line[line.index('元器件厂') + 1]
                    self.rels_unitOrg_componentOrg.append([unit_org, component_org])

                if '元器件厂' in line and '元器件' in line:
                    component_org = line[line.index('元器件厂') + 1]
                    component_name = line[line.index('元器件') + 1]
                    self.components_cats += [component_name]
                    self.rels_componentOrg_component.append([component_org, component_name])

                if '型号' in line and '系统' in line:
                    weapon_name = line[line.index('型号') + 1]
                    system_name = line[line.index('系统') + 1]
                    self.rels_weapon_system.append([weapon_name, system_name])

                if '系统' in line and '部件' in line:
                    system_name = line[line.index('系统') + 1]
                    unit_name = line[line.index('部件') + 1]
                    self.systems_entity += [system_name]
                    self.units_entity += [unit_name]
                    self.rels_weapon_system.append([system_name, unit_name])

                if '部件' in line and '故障元器件' in line:
                    unit_name = line[line.index('部件') + 1]
                    component_name = line[line.index('故障元器件') + 1]
                    self.components_cats += [component_name]
                    self.rels_weapon_system.append([unit_name, component_name])

                if '故障元器件' in line and '元器件故障' in line:
                    com_cats = line[line.index('故障元器件') + 1]
                    fault_component = line[line.index('元器件故障') + 1]
                    self.malfunctions_entity += [fault_component]
                    self.rels_comCats_malfunction.append([com_cats, fault_component])

                if '型号' in line and '主管单位' in line:
                    weapon_name = line[line.index('型号') + 1]
                    charger_name = line[line.index('主管单位') + 1]
                    self.weapon_chargers += [charger_name]  # 武器主管单位
                    self.rels_weapon_charger.append([weapon_name, weapon_name])

                if '主管单位' in line and '处理措施' in line:
                    charger_name = line[line.index('主管单位') + 1]
                    charger_action = line[line.index('处理措施') + 1]
                    self.charger_actions += [charger_action]  # 武器主管单位
                    self.rels_charger_action.append([charger_name, charger_action])

                if '型号' in line and '型号故障' in line:
                    weapon_name = line[line.index('型号') + 1]
                    weapon_fault = line[line.index('型号故障') + 1]
                    self.malfunctions_entity += [weapon_fault]  # 武器级故障
                    self.rels_weapon_fault.append([weapon_name, weapon_fault])

                if '故障系统' in line and '型号故障' in line:
                    weapon_fault = line[line.index('型号故障') + 1]
                    weapon_system = line[line.index('故障系统') + 1]
                    self.rels_weapon_fault.append([weapon_fault, weapon_system])

                if '故障系统' in line and '故障部件' in line:
                    weapon_system = line[line.index('故障系统') + 1]
                    weapon_unit = line[line.index('故障部件') + 1]
                    self.rels_system_unit.append([weapon_system, weapon_unit])

                if '部件' in line and '试验类型' in line and '试验厂所' in line and '试验项' in line and '故障元器件' in line:
                    weapon_unit = line[line.index('部件') + 1]
                    test_type = line[line.index('试验类型') + 1]
                    test_org = line[line.index('试验厂所') + 1]
                    test_name = line[line.index('试验项') + 1]
                    component_fault = line[line.index('故障元器件') + 1]
                    self.test_types += [test_type]
                    self.test_orgs += [test_org]
                    self.test_names += [test_name]
                    self.rels_unit_testType.append([weapon_unit, test_type])
                    self.rels_testType_testOrg.append([test_type, test_org])
                    self.rels_testOrg_testName.append([test_org, test_name])
                    self.rels_testName_componentFault.append([test_name, component_fault])

                if '型号' in line and '使用方' in line and '使用环境' in line and '故障元器件' in line:
                    weapon_name = line[line.index('型号') + 1]
                    weapon_user = line[line.index('使用方') + 1]
                    weapon_use_env = line[line.index('使用环境') + 1]
                    component_fault = line[line.index('故障元器件') + 1]

                    self.weapon_users += [weapon_user]
                    self.weapon_useEnvs += [weapon_use_env]

                    self.rels_weapon_user.append([weapon_name, weapon_user])
                    self.rels_user_useEnv.append([weapon_user, weapon_use_env])
                    self.rels_useEnv_componentFault.append([weapon_use_env, component_fault])

                if '元器件故障' in line and '故障原因' in line and '使用方' in line:
                    component_fault = line[line.index('元器件故障') + 1]
                    fault_cause = line[line.index('故障原因') + 1]
                    weapon_user = line[line.index('使用方') + 1]
                    self.rels_componentFault_faultcause.append([component_fault, fault_cause])  # 元器件故障-故障原因
                    self.rels_faultcause_user.append([fault_cause, weapon_user])

    '''建立没有属性的实体节点'''
    def create_node(self, label, nodes):
        # 去重处理
        # set_nodes = set(nodes)
        print(len(nodes))
        # for name in set_nodes:
        for name in nodes:
            node = Node(label, name=name)
            self.g.create(node)
        return

    '''创建实体关联边'''
    def create_relationship(self, start_label, end_lable, edges, rel_lable, rel_value):
        # 去重处理
        set_edges = []
        for edge in edges:
            set_edges.append('-->'.join(edge))
        set_edges = set(set_edges)
        print(len(set_edges))
        # print("#############################################")
        # print(set_edges)
        # print("#############################################")
        # bound = len(set_edges)
        for edge in set_edges:
            edge = edge.split('-->')
            p = edge[0]
            q = edge[1]
            # print("#############################################")
            # print(p)
            # print(q)
            # print(start_node)
            # print(end_node)
            # print("#############################################")
            query = "match(p:%s),(q:%s) where p.type='%s' and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)"\
                    % (start_label, end_lable, p, q, rel_lable, rel_value)
            try:
                self.g.run(query)
            except Exception as e:
                print(e)
        return

    '''创建知识图谱中武器的节点'''
    def create_weapons_nodes(self):
        print(len(self.weapon_infos))
        for weapon_dict in self.weapon_infos:
            node = Node("weapons", name=weapon_dict['name'], desc=weapon_dict['desc'],
                        flightV=weapon_dict['flightV'], length=weapon_dict['length'],
                        wing=weapon_dict['wing'], max_V=weapon_dict['max_V'],
                        max_L=weapon_dict['max_L'])
            self.g.create(node)
        return

    '''创建知识图谱中元器件的节点'''  # 在这里定义一个节点的全部属性
    def create_components_nodes(self):
        print(len(self.components_infos))
        for component_infos in self.components_infos:
            query = "CREATE (c:components { name: '%s', type: '%s' " \
                    % (component_infos['name'], component_infos['type'])
            if 'quality' in component_infos:
                query += ", quality: '%s'" % (component_infos['quality'])
            if 'encap_mode' in component_infos:
                query += ", encap_mode: '%s'" % (component_infos['encap_mode'])
            if 'desc' in component_infos:
                query += ", desc: '%s'" % (component_infos['desc'])
            if 'tmp_char' in component_infos:
                query += ", tmp_char: %s" % (component_infos['tmp_char'])
            if 'tmp_lower' in component_infos:
                query += ", tmp_lower: %s" % (component_infos['tmp_lower'])
            if 'tmp_upper' in component_infos:
                query += ", tmp_upper: %s" % (component_infos['tmp_upper'])
            if 'res_lower' in component_infos:
                query += ", res_lower: %s" % (component_infos['res_lower'])
            if 'res_upper' in component_infos:
                query += ", res_upper: %s" % (component_infos['res_upper'])
            if 'power' in component_infos:
                query += ", power: %s" % (component_infos['power'])
            if 'weight' in component_infos:
                query += ", weight: %s" % (component_infos['weight'])
            if 'size' in component_infos:
                query += ", size: %s" % (component_infos['size'])
            query += '})'
            try:
                self.g.run(query)
            except Exception as e:
                print(e)
            # node = Node("components_id",
            #             name =component_infos['name'],
            #             identifier=component_infos['ID'],
            #             quality=component_infos['quality'],
            #             # colorLevel=component_infos['colorLevel'],
            #             encap_mode=component_infos['encap_mode'],
            #             desc=component_infos['desc'],
            #             tmp_char=component_infos['tmp_char'],
            #             tmp_lower=component_infos['tmp_lower'],
            #             tmp_upper=component_infos['tmp_upper'],
            #             res_lower=component_infos['res_lower'],
            #             res_upper=component_infos['res_upper'],
            #             power=component_infos['power'],
            #             weight=component_infos['weight'],
            #             size=component_infos['size']
            #             ) # TODO：这里可不可以省缺啊！！！
            # self.g.create(node)
        return

    def create_components_cities(self):
        print(len(self.components_city_i))
        for city in self.components_city_i:
            node = Node("components_city", name = city['name'], China = city['China'])
            try:
                self.g.create(node)
            except Exception as e:
                print(e)
        return

    def create_components_cates(self):
        print(len(self.components_city_i))
        for cate in self.components_cats_i:
            query = "CREATE (c:components_cats { name: '%s' " % cate['name']
            if 'type' in cate:
                query += ", type: '%s'" % (cate['type'])

            query += '})'
            try:
                self.g.run(query)
            except Exception as e:
                print(e)
        return

    '''创建知识图谱实体节点类型schema'''
    def create_graphnodes(self):
        print("create compents:", end='')
        self.create_components_nodes()
        print("create categories:", end='')
        self.create_components_cates()
        print("create cities:", end='')
        self.create_components_cities()
        # print("create weapons:", end=''),
        # self.create_weapons_nodes()
        # # 创建weapon中没有属性的实体
        # print("create weapons_types:", end='')
        # self.create_node('weapons_types', self.weapons_types)
        # print("create weapons_cats:", end='')
        # self.create_node('weapons_cats', self.weapons_cats)
        # print("create weapons_country:", end='')
        # self.create_node('weapons_country', self.weapons_country)
        # print("create weapons_organizations:", end='')
        # self.create_node('weapons_organizations', self.weapons_organizations)
        #
        # # 创建fault中没有属性的实体
        # print("create units_entity:", end='')
        # self.create_node('units_entity', self.units_entity)
        # print("create systems_entity:", end='')
        # self.create_node('systems_entity', self.systems_entity)
        # print("create malfunctions_entity:", end='')
        # self.create_node('malfunctions_entity', self.malfunctions_entity)

        # 创建component中没有属性的实体
        # print("create components_cats:", end='')
        # self.create_node('components_cats', self.components_cats)
        # print("create components_city:", end='')
        # self.create_node('components_city', self.components_city)
        print("create components_organizations:", end='')
        self.create_node('components_organizations', self.components_organizations)

        # # 创建复杂关系数据集中的无属性实体
        # print("create weapon_chargers:", end='')
        # self.create_node('weapon_chargers', self.weapon_chargers)
        # print("create unit_orgs:", end='')
        # self.create_node('unit_orgs', self.unit_orgs)
        # print("create charger_actions:", end='')
        # self.create_node('charger_actions', self.charger_actions)
        # print("create test_types:", end='')
        # self.create_node('test_types', self.test_types)
        # print("create test_orgs:", end='')
        # self.create_node('test_orgs', self.test_orgs)
        # print("create test_names:", end='')
        # self.create_node('test_names', self.test_names)
        # print("create weapon_users:", end='')
        # self.create_node('weapon_users', self.weapon_users)
        # print("create weapon_useEnvs:", end='')
        # self.create_node('weapon_useEnvs', self.weapon_useEnvs)
        # return

    '''创建实体关系边'''
    def create_graphrels(self):
        # weapon中的关系创建
        # print("create 生产国家:", end='')
        # self.create_relationship('weapons', 'weapons_country', self.rels_weapon_country,
        #                          'rels_weapon_country', '生产国家')
        # print("create 武器厂商:", end='')
        # self.create_relationship('weapons', 'weapons_organizations', self.rels_weapon_organization,
        #                          'rels_weapon_organization', '武器厂商')
        # print("create 武器类型:", end='')
        # self.create_relationship('weapons', 'weapons_types', self.rels_weapon_type,
        #                          'rels_weapon_type', '武器类型')
        # print("create 武器大类:", end='')
        # self.create_relationship('weapons_types', 'weapons_cats', self.rels_type_weaCats,
        #                          'rels_type_weaCats', '武器大类')

        # component中的关系创建
        print("create 生产地域:", end='')
        self.create_relationship('components', 'components_city', self.rels_component_city,
                                 'rels_component_city', '生产地域')
        print("create 元器件厂商:", end='')
        self.create_relationship('components', 'components_organizations', self.rels_component_organization,
                                 'rels_component_organization', '元器件厂商')
        print("create 元器件类型:", end='')
        self.create_relationship('components', 'components_cats', self.rels_component_comCats,
                                 'rels_component_comCats', '元器件类型')

        # # fault中的关系创建
        # print("create 系统-部件:", end='')
        # self.create_relationship('systems_entity', 'units_entity', self.rels_system_unit,
        #                          'rels_system_unit', '系统-部件')
        # print("create 武器-系统:", end='')
        # self.create_relationship('weapons', 'systems_entity', self.rels_weapon_system,
        #                          'rels_weapon_system', '武器-系统')
        # print("create 部件-故障:", end='')
        # self.create_relationship('units_entity', 'malfunctions_entity', self.rels_unit_fault,
        #                          'rels_unit_fault', '部件-故障')
        # print("create 元器件-故障:", end='')
        # self.create_relationship('components_cats', 'malfunctions_entity', self.rels_comCats_malfunction,
        #                          'rels_comCats_malfunction', '元器件-故障')
        # print("create 部件-元器件:", end='')
        # self.create_relationship('units_entity', 'components_cats', self.rels_unit_comCats,
        #                          'rels_unit_comCats', '部件-元器件')
        # print("create 武器厂商-部件厂商:", end='')
        # self.create_relationship('weapons_organizations', 'unit_orgs', self.rels_weaponOrg_unitOrg,
        #                          'rels_weaponOrg_unitOrg', '武器厂商-部件厂商')
        # print("create 武器厂商-部件厂商:", end='')
        # self.create_relationship('unit_orgs', 'components_organizations', self.rels_unitOrg_componentOrg,
        #                          'rels_unitOrg_componentOrg', '武器厂商-部件厂商')
        # print("create 元器件厂-元器件:", end='')
        # self.create_relationship('components_organizations', 'components_cats', self.rels_componentOrg_component,
        #                          'rels_componentOrg_component', '元器件厂-元器件')
        # print("create 武器-故障:", end='')
        # self.create_relationship('weapons', 'malfunctions_entity', self.rels_weapon_fault,
        #                          'rels_weapon_fault', '武器-故障')
        # print("create 部件-测试类型:", end='')
        # self.create_relationship('units_entity', 'test_types', self.rels_unit_testType,
        #                          'rels_unit_testType', '部件-测试类型')
        # print("create 测试类型-试验机构:", end='')
        # self.create_relationship('test_types', 'test_orgs', self.rels_testType_testOrg,
        #                          'rels_testType_testOrg', '测试类型-试验机构')
        # print("create 试验机构-测试项:", end='')
        # self.create_relationship('test_orgs', 'test_names', self.rels_testOrg_testName,
        #                          'rels_testOrg_testName', '试验机构-测试项')
        # print("create 测试项-元器件类:", end='')
        # self.create_relationship('test_names', 'components_cats', self.rels_testName_componentFault,
        #                          'rels_testName_componentFault', '测试项-元器件类')
        # print("create 武器-武器使用单位:", end='')
        # self.create_relationship('weapons', 'weapon_users', self.rels_weapon_user,
        #                          'rels_weapon_user', '武器-武器使用单位')
        # print("create 武器使用单位-武器使用环境:", end='')
        # self.create_relationship('weapon_users', 'weapon_useEnvs', self.rels_user_useEnv,
        #                          'rels_user_useEnv', '武器使用单位-武器使用环境')
        # print("create 武器使用环境-故障元器件:", end='')
        # self.create_relationship('weapon_useEnvs', 'components_cats', self.rels_useEnv_componentFault,
        #                          'rels_useEnv_componentFault', '武器使用环境-故障元器件')
        # print("create 元器件故障-故障原因:", end='')
        # self.create_relationship('malfunctions_entity', 'fault_causes', self.rels_componentFault_faultcause,
        #                          'rels_componentFault_faultcause', '元器件故障-故障原因')
        # print("create 故障原因-武器使用单位:", end='')
        # self.create_relationship('fault_causes', 'weapon_users', self.rels_faultcause_user,
        #                          'rels_faultcause_user', '故障原因-武器使用单位')

        return

    '''导出数据'''
    def export_data(self):
        # weapon类的实体词典
        # f_weapons_entity = open('weapons_entity.txt', 'w+', encoding='UTF-8')
        # f_weapons_types = open('weapons_types.txt', 'w+', encoding='UTF-8')
        # f_weapons_cats = open('weapons_cats.txt', 'w+', encoding='UTF-8')
        # f_weapons_country = open('weapons_country.txt', 'w+', encoding='UTF-8')
        # f_weapons_organizations = open('weapons_organizations.txt', 'w+', encoding='UTF-8')
        #
        # f_weapons_entity.write('\n'.join(list(self.weapons_entity)))
        # f_weapons_types.write('\n'.join(list(self.weapons_types)))
        # f_weapons_cats.write('\n'.join(list(self.weapons_cats)))
        # f_weapons_country.write('\n'.join(list(self.weapons_country)))
        # f_weapons_organizations.write('\n'.join(list(self.weapons_organizations)))
        #
        # f_weapons_entity.close()
        # f_weapons_types.close()
        # f_weapons_cats.close()
        # f_weapons_country.close()
        # f_weapons_organizations.close()
        user_dict = []
        for i in self.components_cats:
            user_dict.append('%s 1000 cats' % i)
        for i in self.components_city:
            user_dict.append('%s 1000 city' % i)
        for i in self.components_organizations:
            user_dict.append('%s 1000 org' % i)

        for i in self.components_entity:
            user_dict.append('%s 1000 vtype' % i)
        for i in self.components_quality:
            user_dict.append('%s 1000 vquality' % i)
        for i in self.components_name:
            if ' ' not in i:
                user_dict.append('%s 1000 vname' % i)
        for i in self.components_encap_mode:
            user_dict.append('%s 1000 vencap_mode' % i)

        '''property'''
        user_dict += ['名称 1000 name']
        user_dict += ['型号 1000 type']
        user_dict += ['质量等级 1000 quality']
        user_dict += ['封装形式 1000 encap_mode']

        user_dict += ['额定功耗 1000 power', '功耗 1000 power']
        user_dict += ['温度特性 1000 tmp_char']
        user_dict += ['重量 1000 weight', '质量 1000 weight']
        user_dict += ['尺寸 1000 size']
        user_dict += ['电阻值 1000 res']  # need extend
        user_dict += ['温度 1000 tmp']    # need extend

        '''compare operator'''
        user_dict += ['小于 10000 opa', '低于 10000 opa', '以下 10000 opa']
        user_dict += ['不超过 10000 opb', '不大于 10000 opb', '不高于 10000 opb']
        user_dict += ['等于 10000 opc', '为 10000 opc', '是 10000 opc']
        user_dict += ['大于 10000 opd', '超过 10000 opd', '高于 10000 opd', '以上 10000 opd']
        user_dict += ['不小于 10000 ope', '不低于 10000 ope']
        user_dict += ['范围 10000 opf']  # 也可以搭配为
        user_dict += ['包含 10000 opg']
        user_dict += ['之间 10000 oph']

        f_user_dict = open('user_dict.txt', 'w+', encoding='UTF-8')
        f_user_dict.write('\n'.join(user_dict))
        f_user_dict.close()
        # component类的实体词典
        # f_components_cats = open('components_cats.txt', 'w+', encoding='UTF-8')
        # f_components_city = open('components_city.txt', 'w+', encoding='UTF-8')
        # f_components_organizations = open('components_organizations.txt', 'w+', encoding='UTF-8')
        #
        # f_components_entity = open('components_entity.txt', 'w+', encoding='UTF-8')
        # f_components_quality = open('components_quality.txt', 'w+', encoding='UTF-8')
        # f_components_name = open('components_name.txt', 'w+', encoding='UTF-8')
        # f_components_encap_mode = open('components_encap_mode.txt', 'w+', encoding='UTF-8')
        #
        # f_components_cats.write('\n'.join(self.components_cats))
        # f_components_entity.write('\n'.join(self.components_entity))
        # f_components_city.write('\n'.join(self.components_city))
        # f_components_organizations.write('\n'.join(self.components_organizations))
        # f_components_quality.write()
        # f_components_name.write()
        # f_components_encap_mode.write()
        #
        # f_components_cats.close()
        # f_components_entity.close()
        # f_components_city.close()
        # f_components_organizations.close()
        #
        # f_components_quality.close()
        # f_components_name.close()
        # f_components_encap_mode.close()
        # 故障类实体词典
        # f_units_entity = open('units_entity.txt', 'w+', encoding='UTF-8')
        # f_systems_entity = open('systems_entity.txt', 'w+', encoding='UTF-8')
        # f_malfunctions_entity = open('malfunctions_entity.txt', 'w+', encoding='UTF-8')
        #
        # f_units_entity.write('\n'.join(list(self.units_entity)))
        # f_systems_entity.write('\n'.join(list(self.systems_entity)))
        # f_malfunctions_entity.write('\n'.join(list(self.malfunctions_entity)))
        #
        # f_units_entity.close()
        # f_systems_entity.close()
        # f_malfunctions_entity.close()

        return


if __name__ == '__main__':
    handler = MilitaryGraph()
    # read data from file
    read_data()
    handler.create_graphnodes()
    handler.create_graphrels()
    handler.export_data()
