import json

import boto3
import pandas


class DescribeApis:

    def __init__(self, region, a_key, s_key):
        self.region = region
        self.access_key = a_key
        self.secret_access_key = s_key

    def createClient(self):
        session = boto3.setup_default_session(aws_access_key_id=self.access_key,
                                              aws_secret_access_key=self.secret_access_key)
        self.client = boto3.client('apigateway', self.region)

    def getAllApis(self):
        response = self.client.get_rest_apis()
        return response

    def getAuthDetails(self, apiId):
        response = self.client.get_authorizers(restApiId=apiId)
        return response

    def getResources(self, apiId):
        response = self.client.get_resources(
            restApiId=apiId
        )
        return response

    def get_result(self):
        output_dict = {}
        methods_list = input("Enter Comma Separated list of Methods, else press enter : ").split(",")
        print("Enter option number:")
        output_format = int(input("1.csv, 2.json-pretty, 3.json : "))
        if output_format not in [1, 2, 3]:
            print("Sorry Incorrect input, exiting ...")
            exit(0)
        self.createClient()
        all_apis = self.getAllApis()
        for items in all_apis['items']:
            id = items["id"]
            print("API NAME : ", items['name'])
            output_dict[items['name']] = {}
            print("\tAPI ID : ", id)
            output_dict[items['name']]["API ID"] = str(id)
            print("\tAPI Description : ", items['description'])
            output_dict[items['name']]["Description"] = items["description"]
            print("\tAPI KEY source : ", items['apiKeySource'])
            output_dict[items['name']]["API Key Source"] = items['apiKeySource']
            auth_details_items = self.getAuthDetails(id)
            if not auth_details_items['items']:
                output_dict[items['name']]["API Authorization"] = "Not Applicable"
                print("\tAPI Authorization : Not Applicable")
            else:
                for api_auth in auth_details_items:
                    print("\tAPI Authorization : ")
                    output_dict[items['name']]["API Authorization"] = api_auth['type']
                    print("\t\tType : ", api_auth['type'])
            print("\tResource Details : ")
            resource_details = self.getResources(id)
            output_dict[items['name']]["Resouce Details"] = {}
            for rditem in resource_details['items']:
                output_dict[items['name']]["Resouce Details"]["Path"] = rditem['path']
                print("\t\tPath : ", rditem['path'])
                output_dict[items['name']]["Resouce Details"]["Path"] = {}
                if "resourceMethods" in rditem:
                    output_dict[items['name']]["Resouce Details"]["Path"]["Resource Methods"] = {}
                    print("\t\t\tResource Methods : ")
                    if methods_list == ['']:
                        for k, v in rditem['resourceMethods'].items():
                            output_dict[items['name']]["Resouce Details"]["Path"]["Resource Methods"][k] = \
                                rditem['resourceMethods'][k]
                            print("\t\t\t\t", k, " : ", rditem['resourceMethods'][k])
                    else:
                        for k, v in rditem['resourceMethods'].items():
                            if k in methods_list:
                                output_dict[items['name']]["Resouce Details"]["Path"]["Resource Methods"][k] = \
                                    rditem['resourceMethods'][k]
                                print("\t\t\t\t", k, " : ", rditem['resourceMethods'][k])


                else:
                    output_dict[items['name']]["Resouce Details"]["Path"][
                        "Resource Methods"] = "No Resource Methods for this path."
                    print("\t\t\tResource Methods : No Resource Methods for this path.")
        if output_format == 3:
            with open('result.json', 'w+') as fp:
                json.dump(output_dict, fp)
        elif output_format == 2:
            pretty = json.dumps(output_dict, indent=4, separators=(',', ': '), sort_keys=True)
            with open('pretty.json', 'w+') as fp:
                json.dump(pretty, fp)

        else:
            df = pandas.DataFrame.from_dict(output_dict, orient="index")
            df.to_csv("results.csv")


if __name__ == '__main__':
    print("Please enter the following information to proceed forward :")
    a_key = input("Enter Access Key")
    if not a_key:
        print("Sorry incorrect input, exiting ...")
    s_key = input("Enter Secret Access Key")
    if not a_key:
        print("Sorry incorrect input, exiting ...")
    region = input("Enter Region")
    if not region:
        print("Sorry incorrect input, exiting ...")
    api_obj = DescribeApis(region, a_key, s_key)
    api_obj.get_result()
