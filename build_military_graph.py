# -*- coding: utf-8 -*-
# @File : build_military_graph.py
# @Time : 3/15/23 14:05
import json
import os
import re
from time import time

from py2neo import Graph, Node, Relationship, Subgraph


class MilitaryGraph:
    military_attributes_in_en = ['name', 'origin_country', 'img_url', 'introduction', 'first_fly_time',
                                 'R&D_organization',
                                 'pneumatic_layout', 'num_of_engine', 'speed', 'attention_degree', 'crew_num',
                                 'flight_long', 'wings_width', 'flight_height', 'engine', 'max_speed', 'max_voyage',
                                 'class', 'categories', 'serve_time', 'producer', 'net_weight', 'max_fly_weight',
                                 'retire_time', 'rotor_diameter', 'machine_gun', 'mount_point', 'built-in_weapon',
                                 'war_field_machine_type', 'W-3W', 'build_time', 'full_tonnage_row', 'authorized',
                                 'captain', 'modeled_breath', 'load_displacement', 'cruising_distance',
                                 'navigational_speed', 'manufactory', 'launch_time', 'status', 'same_type',
                                 'activity_range', 'prior_type', 'latter_type', 'self-sustaining', 'missile',
                                 'cannon', 'modify_time', 'water_displacement', 'firing_control_device', 'main_cannon',
                                 'submersible_depth', 'before_modify', 'complete_time', 'equipment', 'Armed',
                                 'military_uniform', '1935', 'anti-ship_missile', 'ship-to-ship_missile',
                                 'new_build', 'anti-aircraft-weapon', 'under_water_displacement', 'weapon_equipment',
                                 'torpedo', 'mine', 'arms', 'shooter', 'firearms', 'manufacturer', 'produce_year',
                                 'amount', 'calibres',
                                 'gun_length', 'gun_weight', 'magazine_capacity',
                                 'war_participation', 'effective_range', 'shoot_performance', 'shoot_speed',
                                 'knife_length', 'blade_length', 'blade_width', 'knife_weight', 'R&D_manufactures',
                                 'born_time', 'chassis_type', 'crew_num', 'vehicle_length', 'width', 'height',
                                 'weight_in_war', 'max_speed', 'max_route', 'gross_weight', 'barrel_length',
                                 'max_range', 'muzzle_velocity', 'R&D_time', 'editor_rating', 'version', 'tital_length',
                                 'development_time', 'shoot_range', 'bullet_length',
                                 'bullet_diameter',
                                 'bullet_weight', 'guidance_sys', 'fuze', 'launch_date', 'launch_place', 'length',
                                 'center_diameter', 'first_orbital_launch', 'orbit', 'longitude', 'latitude',
                                 'carrier_rocket', 'processor', 'orbiting_satellites', 'charge_type', 'total_weight',
                                 'fuze_device', 'tail_device', 'power_device']
    military_attributes = ['名称', '产国', '图片', '简介', '首飞时间', '研发单位', '气动布局', '发动机数量', '飞行速度',
                           '关注度', '乘员',
                           '机长', '翼展', '机高', '发动机', '最大飞行速度', '最大航程', '大类', '类型', '服役时间',
                           '生产单位',
                           '空重',
                           '最大起飞重量', '退役时间', '旋翼直径', '机炮', '挂载点', '内置武器', '战地机型', 'W-3W',
                           '建造时间',
                           '满排吨位', '编制',
                           '舰长', '型宽', '满载排水量', '续航距离', '航速', '制造厂', '下水时间', '现状', '同型',
                           '活动范围',
                           '前型', '次型',
                           '自持力', '导弹', '火炮', '改装时', '水上排水量', '射控装置', '主炮', '潜航深度', '改装前',
                           '竣工时',
                           '装备', '武备',
                           '兵装', '1935年', '反舰导弹', '舰舰导弹', '新造时', '防空兵器', '水下排水量', '武器装备',
                           '鱼雷',
                           '水雷', '武装',
                           '枪械', '枪炮', '制造商', '生产年限', '数量', '口径', '全枪长', '全枪重', '弹匣容弹量',
                           '参战情况',
                           '有效射程', '发射性能',
                           '战斗射速', '刀长', '刀锋长度', '刀锋宽度', '刀重', '研发厂商', '诞生时间', '底盘类型',
                           '乘员与载员',
                           '车长', '宽度',
                           '高度', '战斗全重', '最大速度', '最大行程', '总重', '炮管长度', '最大射程', '炮口初速',
                           '研发时间',
                           '编辑评分', '型号',
                           '全长', '研制时间', '射程', '弹长', '弹径', '弹重', '制导系统', '引信', '发射日期',
                           '发射地点', '长度',
                           '中心直径',
                           '首次轨道发射', '轨道', '纬度', '经度', '运载火箭', '处理器', '轨道卫星', '装药类型', '全重',
                           '引信装置', '尾翼装置',
                           '动力装置']

    node_attributes = ['产国', '研发单位', '研发厂商', '大类', '类型', '制造商', '制造厂',
                       '活动范围', '底盘类型', '口径', '型号', '气动布局']

    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        self.data_path = os.path.join(cur_dir, 'data/military.json')

    '''读取文件'''

    def read_nodes(self):
        militaries = []  # 武器等
        producing_countries = []  # 产国
        research_and_develop_organizations = []  # 研发单位/研发厂商
        producers = []  # 生产单位/生产厂

        classes = []  # 大类
        categories = []  # 类别

        armored_car_chassis_types = []  # 装甲车底盘类型——装甲车
        vessels_activity_areas = []  # 船的活动范围——船
        pneumatic_layouts = []  # 气动布局——飞行器
        cannon_calibres = []  # 口径——火炮
        cannon_types = []  # 型号——火炮

        militaries_infos = []  # 武器信息

        # 实体之间的关系
        rels_militaries_producing_countries = []  # 武器-产国
        rels_producers_in_producing_countries = []  # 生产商-产国
        rels_country_research_and_develop_organizations = []  # 研发组织-国家
        rels_militaries_research_and_develop_organizations = []  # 武器-研发组织
        rels_militaries_producers = []  # 武器-生产商
        rels_militaries_categories = []  # 武器-类别
        rels_categories_classes = []  # 大类-具体类别
        rels_militaries_armored_car_chassis_type = []  # 武器-装甲车底盘类型（装甲车特有）
        rels_militaries_vessels_activity_area = []  # 武器-船的活动范围（船特有）
        rels_militaries_pneumatic_layout = []  # 武器-气动布局（飞行器）
        rels_militaries_cannon_calibre = []  # 武器-口径（火炮）
        rels_militaries_cannon_type = []  # 武器-型号（火炮）

        count = 0
        for data in open(self.data_path, encoding='utf8'):
            militaries_dict = {}
            count += 1
            data_json = json.loads(data)
            military = data_json['名称']
            militaries_dict['名称'] = military
            militaries.append(military)
            for attr in self.military_attributes:
                if attr in data_json:
                    militaries_dict[attr] = data_json[attr]

            if '产国' in data_json:
                country = data_json['产国']
                producing_countries.append(country)
                rels_militaries_producing_countries.append([military, country])

            if '研发单位' in data_json:
                research_and_develop_organization = data_json['研发单位']
                research_and_develop_organizations.append(research_and_develop_organization)
                rels_militaries_research_and_develop_organizations.append([military, research_and_develop_organization])
                if '产国' in data_json:
                    country = data_json['产国']
                    if [country,
                        research_and_develop_organization] not in rels_country_research_and_develop_organizations:
                        rels_country_research_and_develop_organizations.append(
                            [research_and_develop_organization, country])

            if '研发厂商' in data_json:
                research_and_develop_organization = data_json['研发厂商']
                research_and_develop_organizations.append(research_and_develop_organization)
                rels_militaries_research_and_develop_organizations.append([military, research_and_develop_organization])
                if '产国' in data_json:
                    country = data_json['产国']
                    if [country,
                        research_and_develop_organization] not in rels_country_research_and_develop_organizations:
                        rels_country_research_and_develop_organizations.append(
                            [research_and_develop_organization, country])

            if '大类' in data_json:
                big_class = data_json['大类']
                classes.append(big_class)

            if '类型' in data_json:
                category = data_json['类型']
                categories.append(category)
                rels_militaries_categories.append([military, category])
                if '大类' in data_json:
                    big_class = data_json['大类']
                    if [big_class, category] not in rels_categories_classes:
                        rels_categories_classes.append([category, big_class])

            if '制造商' in data_json:
                producer = data_json['制造商']
                producers.append(producer)
                rels_militaries_producers.append([military, producer])
                if '产国' in data_json:
                    country = data_json['产国']
                    if [country, producer] not in rels_producers_in_producing_countries:
                        rels_producers_in_producing_countries.append([producer, country])

            if '制造厂' in data_json:
                producer = data_json['制造厂']
                producers.append(producer)
                rels_militaries_producers.append([military, producer])
                if '产国' in data_json:
                    country = data_json['产国']
                    if [country, producer] not in rels_producers_in_producing_countries:
                        rels_producers_in_producing_countries.append([producer, country])

            if '活动范围' in data_json:
                vessels_activity_area = data_json['活动范围']
                if '，' in vessels_activity_area:
                    vessels_activity_area_l = vessels_activity_area.split('，')
                    for item in vessels_activity_area_l:
                        vessels_activity_areas.append(item)
                        rels_militaries_vessels_activity_area.append([military, item])
                elif '、' in vessels_activity_area:
                    vessels_activity_area_l = vessels_activity_area.split('，')
                    for item in vessels_activity_area_l:
                        vessels_activity_areas.append(item)
                        rels_militaries_vessels_activity_area.append([military, item])
                else:
                    vessels_activity_areas.append(vessels_activity_area)
                    rels_militaries_vessels_activity_area.append([military, vessels_activity_area])

            if '底盘类型' in data_json:
                armored_car_chassis_type = data_json['底盘类型']
                armored_car_chassis_types.append(armored_car_chassis_type)
                rels_militaries_armored_car_chassis_type.append([military, armored_car_chassis_type])

            if '气动布局' in data_json:
                pneumatic_layout = data_json['气动布局']
                pneumatic_layouts.append(pneumatic_layout)
                rels_militaries_pneumatic_layout.append([military, pneumatic_layout])

            if '口径' in data_json:
                cannon_calibre = data_json['口径']
                cannon_calibres.append(cannon_calibre)
                rels_militaries_cannon_calibre.append([military, cannon_calibre])

            if '型号' in data_json:
                cannon_type = data_json['型号']
                cannon_types.append(cannon_type)
                rels_militaries_cannon_type.append([military, cannon_type])

            militaries_infos.append(militaries_dict)

        return set(militaries), set(producing_countries), set(research_and_develop_organizations), set(
            producers), set(classes), set(categories), set(armored_car_chassis_types), set(
            vessels_activity_areas), set(pneumatic_layouts), set(cannon_calibres), set(
            cannon_types), militaries_infos, rels_militaries_producing_countries, \
            rels_producers_in_producing_countries, rels_country_research_and_develop_organizations, \
            rels_militaries_research_and_develop_organizations, rels_militaries_producers, \
            rels_militaries_categories, rels_categories_classes, rels_militaries_armored_car_chassis_type, \
            rels_militaries_vessels_activity_area, rels_militaries_pneumatic_layout, \
            rels_militaries_cannon_calibre, rels_militaries_cannon_type

    '''建立节点'''

    def create_node(self, label, nodes):
        count = 0
        nodess = []
        for node_name in nodes:
            count += 1
            node = Node(label, name=node_name)
            node['id'] = count
            nodess.append(node)
        return nodess

    '''创建military节点'''

    def create_military_node(self, militaries_infos):
        count = 0
        nodes = []
        military_attributes_dict = {}
        cnt = len(self.military_attributes)
        for i in range(cnt):
            military_attributes_dict[self.military_attributes[i]] = self.military_attributes_in_en[i]
        for militaries_dict in militaries_infos:
            count += 1
            node = Node("Military")
            node['id'] = count
            for attr in self.military_attributes:
                if attr in militaries_dict:
                    node[military_attributes_dict[attr]] = militaries_dict[attr]
            nodes.append(node)
        return nodes

    '''创建知识图谱实体节点类型schema'''

    def create_graph_nodes(self):
        Militaries, Producing_countries, Research_and_develop_organizations, Producers, Classes, Categories, \
            Armored_car_chassis_types, Vessels_activity_areas, Pneumatic_layouts, Cannon_calibres, Cannon_types, \
            militaries_infos, rels_militaries_producing_countries, \
            rels_producers_in_producing_countries, rels_country_research_and_develop_organizations, \
            rels_militaries_research_and_develop_organizations, rels_militaries_producers, \
            rels_militaries_categories, rels_categories_classes, rels_militaries_armored_car_chassis_type, \
            rels_militaries_vessels_activity_area, rels_militaries_pneumatic_layout, \
            rels_militaries_cannon_calibre, rels_militaries_cannon_type = self.read_nodes()
        a = self.create_military_node(militaries_infos)
        b = self.create_node('Country', Producing_countries)
        c = self.create_node('Research_and_develop_organization', Research_and_develop_organizations)
        d = self.create_node('Producer', Producers)
        e = self.create_node('Class', Classes)
        f = self.create_node('Category', Categories)
        g = self.create_node('Armored_car_chassis_type', Armored_car_chassis_types)
        h = self.create_node('Vessels_activity_area', Vessels_activity_areas)
        i = self.create_node('Pneumatic_layout', Pneumatic_layouts)
        j = self.create_node('Cannon_calibre', Cannon_calibres)
        k = self.create_node('Cannon_type', Cannon_types)
        return a + b + c + d + e + f + g + h + i + j + k

    '''创建实体关联边'''

    def create_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        count = 0
        # 去重处理
        relationships = []
        set_edges = []
        for edge in edges:
            set_edges.append('###'.join(edge))
        all = len(set(set_edges))
        for edge in set(set_edges):
            edge = edge.split('###')
            p = edge[0]
            q = edge[1]
            query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
                start_node, end_node, p, q, rel_type, rel_name)
            relationships.append(query)
            try:
                count += 1
            except Exception as e:
                print()
        return relationships

    '''创建实体关系边'''

    def create_graph_rels(self):
        Militaries, Producing_countries, Research_and_develop_organizations, Producers, Classes, Categories, \
            Armored_car_chassis_types, Vessels_activity_areas, Pneumatic_layouts, Cannon_calibres, Cannon_types, \
            militaries_infos, rels_militaries_producing_countries, \
            rels_producers_in_producing_countries, rels_country_research_and_develop_organizations, \
            rels_militaries_research_and_develop_organizations, rels_militaries_producers, \
            rels_militaries_categories, rels_categories_classes, rels_militaries_armored_car_chassis_type, \
            rels_militaries_vessels_activity_area, rels_militaries_pneumatic_layout, \
            rels_militaries_cannon_calibre, rels_militaries_cannon_type = self.read_nodes()
        a = self.create_relationship('Military', 'Country', rels_militaries_producing_countries,
                                     'producing_country', '产国')  # Military --> Country
        b = self.create_relationship('Producer', 'Country', rels_producers_in_producing_countries,
                                     'producer_in_country', '制造商所属国家')  # Producer --> Country
        c = self.create_relationship('Research_and_develop_organization', 'Country',
                                     rels_country_research_and_develop_organizations, 'RandD_organization_in_country',
                                     '研发厂商所属国家')  # R&D Organization --> Country
        d = self.create_relationship('Military', 'Research_and_develop_organization',
                                     rels_militaries_research_and_develop_organizations, 'Military2RandD_organization',
                                     '研发组织')  # Military --> R&D Organization
        e = self.create_relationship('Military', 'Producer', rels_militaries_producers, 'Military2Producer',
                                     '制造厂')  # Military --> Producer
        f = self.create_relationship('Military', 'Category', rels_militaries_categories, 'Category',
                                     '具体类别')  # Military --> Category
        g = self.create_relationship('Category', 'Class', rels_categories_classes, 'Category_in_Class',
                                     '大类-小类')  # Category --> Class
        h = self.create_relationship('Military', 'Armored_car_chassis_type', rels_militaries_armored_car_chassis_type,
                                     'chassis_type', '装甲车的底盘类型')  # Military --> Armored_car_chassis_type
        i = self.create_relationship('Military', 'Vessels_activity_area', rels_militaries_vessels_activity_area,
                                     'activity_area', '轮船的活动范围')  # Military --> Vessels_activity_area
        j = self.create_relationship('Military', 'Pneumatic_layout', rels_militaries_pneumatic_layout,
                                     'pneumatic_layout', '飞行器的气动布局')  # Military --> Pneumatic_layout
        k = self.create_relationship('Military', 'Cannon_calibre', rels_militaries_cannon_calibre, 'cannon_calibre',
                                     '火炮的口径')  # Military --> Cannon_calibre
        l = self.create_relationship('Military', 'Cannon_type', rels_militaries_cannon_type, 'cannon_type',
                                     '火炮的类型')  # Military --> Cannon_type

        return a + b + c + d + e + f + g + h + i + j + k + l


BAR = True
t0 = time()


class ProgressBar:
    def __init__(self, total, name='', mode=0):
        self.total = total
        self.name = name
        modes = (
            lambda n: f"进度|{'=' * n}{'>'}{'·' * (100 - n)}"[:-1] + f"| {n}% |",
            lambda n: f"进度|{'█' * n:100s}| {n}% |",
            lambda n: f"\033[31m{'♥' * n}{'♡' * (100 - n)}  进度{n}♥\033[0m",
            lambda n: f"\033[46m进度{' ' * n}{n}% \033[44m{' ' * (100 - n)}\033[0m",
        )
        mode = 0 if mode > 3 else mode
        self.mode = modes[mode]

    def now(self, n):
        if BAR:
            n_ = 100 * n // self.total
            print(f"\r{self.name}: {self.mode(n_)} [{n:05d} / {self.total}]", end='', flush=True)

    def end(self, name):
        print(name)


if __name__ == '__main__':
    handler = MilitaryGraph()
    graph_nodes = handler.create_graph_nodes()
    graph_rels = handler.create_graph_rels()
    print(f"匹配所用时间：{time() - t0:.1f}秒")
    print('正在创建图谱 . . . . . .', end='')
    # graph = Graph("bolt://localhost:7687", username="neo4j", password="neo4j", name="Military")
    graph = Graph("bolt://localhost:7687", username="neo4j", password="neo4j")
    # 版本 20201.
    dicts = {}
    for i in graph_nodes:
        dicts[i['name']] = i
    import numpy as np

    len(np.array(graph_rels))
    p = ProgressBar(len(np.array(graph_rels)), '匹配进度', mode=3)
    s = 0
    relationships = []
    for i in graph_rels:
        p.now(s)
        n1 = i.split("p.name=")[1].split("and q.name=")[0]
        n = n1[1:-1]
        m1 = i.split("and q.name=")[1].split(" create (p)-[rel")[0]
        m = m1[1:-1]
        rr = i.split('[')[-1].split(']')[0][4:].split("'")[1]
        r = i.split('[')[-1].split(':')[1].split('{')[0]
        relationships.append(Relationship(dicts[n], r, dicts[m], name=rr))
        s += 1

    print(f"匹配所用时间：{time() - t0:.1f}秒")
    print('数据正在导入数据库......')

    graph.create(Subgraph(nodes=graph_nodes, relationships=relationships))

    print('\r知识图谱数据库创建完成 !!')
    print(f"总体所用时间：{time() - t0:.1f}秒")
