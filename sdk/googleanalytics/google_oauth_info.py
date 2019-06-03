# -*-coding:utf-8-*-
import sys
from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials


class GoogleApi():
    def __init__(self, view_id, json_path=""):
        """
        获取店铺的GA数据
        :param view_id: 视图的id
        :param key_words: 来源的关键字
        """
        self.SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
        if json_path:
            self.KEY_FILE_LOCATION = json_path
        else:
            self.KEY_FILE_LOCATION = 'client_secrets.json'
        self.VIEW_ID = view_id

    def get_report(self, key_words, start_time, end_time):
        """
         Queries the Analytics Reporting API V4.
        Args:
          analytics: An authorized Analytics Reporting API V4 service object.
        Returns:
          The Analytics Reporting API V4 response.
        """
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.KEY_FILE_LOCATION, self.SCOPES)
        # Build the service object.
        analytics = discovery.build('analyticsreporting', 'v4', credentials=credentials)
        analytics_info = analytics.reports().batchGet(
            body={
                "reportRequests":
                    [
                        {
                            "viewId": self.VIEW_ID,
                            "dateRanges": [
                                {'startDate': start_time, 'endDate': end_time},
                            ],
                            "metrics": [
                                {"expression": "ga:pageviews"},  # pv
                                {"expression": "ga:uniquePageviews"},  # uv
                                {"expression": "ga:hits"},  # 点击量
                                {"expression": "ga:transactions"}  # 交易数量
                            ],
                            "dimensions": [
                                {"name": "ga:source"},
                            ],
                            # "dimensionFilterClauses": [
                            #     {
                            #         "filters": [
                            #             {
                            #                 "dimensionName": "ga:source",
                            #                 "operator": "EXACT",
                            #                 "expressions": ["baidu"]
                            #             }]
                            #         }]
                             }]
                            }).execute()
        statistics_info = []
        for report in analytics_info.get('reports', []):
            columnHeader = report.get('columnHeader', {})
            dimensionHeaders = columnHeader.get('dimensions', [])
            metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

            for row in report.get('data', {}).get('rows', []):
                dimensions = row.get('dimensions', [])
                dateRangeValues = row.get('metrics', [])
                for header, dimension in zip(dimensionHeaders, dimensions):
                    if key_words in dimension:
                        for i, values in enumerate(dateRangeValues):
                            for metricHeader, value in zip(metricHeaders, values.get('values')):
                                shop_info = metricHeader.get('name').replace("ga:", "") + ', ' + value
                                f = shop_info.split(",")
                                statistics_info.append(f)

        data = dict(statistics_info)
        for key in data.keys():
            data[key] = float(data[key].strip()) if key=="transactions" else int(data[key].strip())
        print(data)
        return {"code": 1, "date": data, "msg": ""}


if __name__ == '__main__':
    google_data = GoogleApi(view_id="195406097")
    google_data.get_report(key_words="google", start_time="30daysAgo", end_time="today")


