"""Hello Analytics Reporting API V4."""

from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials


class GoogleApi():
    def __init__(self, view_id):
        self.SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
        self.KEY_FILE_LOCATION = 'client_secrets.json'
        self.VIEW_ID = view_id

    def initialize_analyticsreporting(self):
        """
          Initializes an Analytics Reporting API V4 service object.
        Returns:
          An authorized Analytics Reporting API V4 service object.
        """
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.KEY_FILE_LOCATION, self.SCOPES)
        # Build the service object.
        analytics = discovery.build('analyticsreporting', 'v4', credentials=credentials)
        return analytics

    def get_report(self, analytics):
        """Queries the Analytics Reporting API V4.
        Args:
          analytics: An authorized Analytics Reporting API V4 service object.
        Returns:
          The Analytics Reporting API V4 response.
        """
        return analytics.reports().batchGet(
            body={
                "reportRequests":
                    [
                        {
                            "viewId": self.VIEW_ID,
                            "dateRanges": [
                                {'startDate': '15daysAgo', 'endDate': 'today'},
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

    def print_response(self, response):
        """Parses and prints the Analytics Reporting API V4 response.

        Args:
          response: An Analytics Reporting API V4 response.
        """
        for report in response.get('reports', []):
            columnHeader = report.get('columnHeader', {})
            dimensionHeaders = columnHeader.get('dimensions', [])
            metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

            for row in report.get('data', {}).get('rows', []):
                dimensions = row.get('dimensions', [])
                dateRangeValues = row.get('metrics', [])
                for header, dimension in zip(dimensionHeaders, dimensions):
                    print(header + ': ' + dimension)

                for i, values in enumerate(dateRangeValues):
                    print('Date range: ' + str(i))
                    for metricHeader, value in zip(metricHeaders, values.get('values')):
                        print(metricHeader.get('name') + ': ' + value)

    def main(self):
        analytics = self.initialize_analyticsreporting()
        response = self.get_report(analytics)
        response_data = self.print_response(response)


if __name__ == '__main__':
    google_data = GoogleApi(view_id="195406097")
    google_data.main()


