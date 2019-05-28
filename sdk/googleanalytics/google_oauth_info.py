"""Hello Analytics Reporting API V4."""

from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials


class GoogleApi():
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
        self.KEY_FILE_LOCATION = 'client_secrets.json'
        self.VIEW_ID = '195406097'

    def initialize_analyticsreporting(self):
        """Initializes an Analytics Reporting API V4 service object.
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
                                # {'startDate': '7daysAgo', 'endDate': 'today'},
                                {"startDate": "1daysAgo", "endDate": "1daysAgo"}
                            ],
                            "metrics": [
                                {"expression": "ga:pageviews"},
                                {"expression": "ga:sessions"}
                            ],
                            "dimensions": [{"name": "ga:browser"}, {"name": "ga:country"}],
                            "dimensionFilterClauses": [
                                {
                                    "filters": [
                                        {
                                            "dimensionName": "ga:browser",
                                            "operator": "EXACT",
                                            "expressions": ["Chrome"]
                                        }]
                                   }]
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
        print(response_data)


if __name__ == '__main__':
    google_data = GoogleApi()
    google_data.main()


