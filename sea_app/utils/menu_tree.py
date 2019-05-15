from sea_app import models


class MenuTree(object):

    def __init__(self, user):
        self.user = user
        self.memu_str = ""
        self.menu_dict = {}
        self.menu_list = []
        self.route_list = []

    def crate_menu_tree(self):
        menuid_list = eval(self.user.role.menu_list)
        menu_list = models.Menu.objects.filter(id__in=menuid_list).values("id", "menu_name", "menu_url", "parent_id", "icon").order_by("menu_num")
        for row in menu_list:
            if "/" in row["menu_url"]:
                print(row)
                self.route_list.append({"path": row["menu_url"], "name": row["menu_name"], "component": row["menu_name"]})
            row["childs"] = []
            if row['parent_id']:
                self.menu_dict[row['parent_id']]['childs'].append(row)
            self.menu_dict[row["id"]] = row

        for key, val in self.menu_dict.items():
            if not val["parent_id"]:
                self.menu_list.append(val)
        return self.menu_list, self.route_list
