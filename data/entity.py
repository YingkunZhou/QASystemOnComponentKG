# 实体
# 装备级实体
global weapons_cats = []  # 武器大类
global weapons_types = []  # 武器类型
global weapons_entity = []  # 武器实体
global weapons_infos = []  # 武器实体信息

# 系统级实体
global systems_entity = []  # 系统实体
global systems_infos = []  # 系统实体信息

# 部件级实体
global units_entity = []  # 部件实体
global units_infos = []  # 部件实体信息

# 元器件级实体
global components_entity = []  # 元器件
global components_cats = []  # 元器件分类
global components_infos = []  # 元器件实体信息

# 故障实体
global malfunctions_entity = []  # 部件级故障
global malfunctions_infos = []  # 故障实体信息

# 其他实体
global weapons_country = []  # 武器产国
global weapons_organizations = []  # 武器产商
global components_city = []  # 元器件生产城市
global components_organizations = []  # 元器件生产厂家

# 关系
global rels_weapon_country = []  # 武器-产国从属关系
global rels_weapon_organization = []  # 武器-研发机构从属关系
global rels_weapon_type = []  # 武器－类型的关系
global rels_type_weaCats = []  # 类型-大类的关系

global rels_component_city = []  # 元器件-生产城市从属关系
global rels_component_organization = []  # 元器件-产商从属关系
global rels_component_comCats = []  # 元器件-类型从属关系
global rels_comCats_malfunction = []  # 元器件类-故障的关系
global rels_unit_fault = []  # 部件-故障关系
global rels_system_unit = []  # 部件-系统关系
global rels_unit_comCats = []  # 部件-元器件类关系
global rels_weapon_system = []  # 武器-系统


显示器黑屏如何处理

问题分类：
system_fault_deal
unit_fault_search


# 加载特征词
        #weapon类特征词
        self.weapons_entity_wds= [i.strip() for i in open(self.weapons_entity_path, encoding='UTF-8') if i.strip()]
        self.weapons_cats_wds= [i.strip() for i in open(self.weapons_cats_path, encoding='UTF-8') if i.strip()]
        self.weapons_organizations_wds= [i.strip() for i in open(self.weapons_organizations_path, encoding='UTF-8') if i.strip()]
        self.weapons_country_wds= [i.strip() for i in open(self.weapons_country_path, encoding='UTF-8') if i.strip()]
        self.weapons_types_wds= [i.strip() for i in open(self.weapons_types_path, encoding='UTF-8') if i.strip()]
        self.region_words = set(self.weapons_entity_wds + self.weapons_cats_wds + self.weapons_organizations_wds + self.weapons_country_wds + self.weapons_types_wds)
        #component类特征词
        self.components_cats_wds = [i.strip() for i in open(self.components_cats_path, encoding='UTF-8') if i.strip()]
        self.components_entity_wds = [i.strip() for i in open(self.components_entity_path, encoding='UTF-8') if i.strip()]
        self.components_city_wds = [i.strip() for i in open(self.components_city_path, encoding='UTF-8') if i.strip()]
        self.components_organizations_wds = [i.strip() for i in open(self.components_organizations_path, encoding='UTF-8') if i.strip()]
        self.region_words += set(self.components_cats_wds + self.components_entity_wds + self.components_city_wds + self.components_organizations_wds)
        #fault类特征词
        self.units_entity_wds = [i.strip() for i in open(self.units_entity_path, encoding='UTF-8') if i.strip()]
        self.systems_entity_wds = [i.strip() for i in open(self.systems_entity_path, encoding='UTF-8') if i.strip()]
        self.malfunctions_entity_wds = [i.strip() for i in open(self.malfunctions_entity_path, encoding='UTF-8') if i.strip()]
        self.region_words += set(self.units_entity_wds + self.systems_entity_wds + self.malfunctions_entity_wds)
		
		
		
		self.weapons_entity_qds = ['武器型号', '飞机型号', '武器', '飞机']
        self.weapons_country_qds = ['产国','产于', '哪里生产', '生产', '产地']
        self.weapons_organizations_qds = ['产商', '生产厂商', '生产机构', '生产商']
        self.weapons_types_qds = ['类别', '类型']
        self.fault_deal_qds = ['处理措施', '如何处理', '怎么办', '怎么处理']#处理措施的问句
		
		
		
		
		
		
self.weapon_chargers, self.charger_actions, self.units_entity, self.test_types, self.test_orgs, self.test_names, self.weapon_users, self. 
self.rels_weaponOrg_unitOrg, self.rels_systemOrg_componentOrg, self.rels_componentOrg_component, self.rels_weapon_system, self.rels_weapon_system, self.rels_weapon_system, self.rels_weapon_charger, self.rels_charger_action, self.rels_weapon_fault, self.rels_weapon_fault, self.rels_system_unit, self.rels_unit_testType, self.rels_testType_testOrg, self.rels_testOrg_testName, self.rels_testName_componentFault, self.rels_weapon_user, self.rels_user_useEnv, self.rels_useEnv_componentFault, self.rels_componentFault_faultcause, self.rels_faultcause_user
        
		
component_name