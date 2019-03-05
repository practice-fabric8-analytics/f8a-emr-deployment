# f8a-emr-deployment

[![Build Status](https://ci.centos.org/job/devtools-f8a-emr-deployment-build-master/badge/icon)](https://ci.centos.org/job/devtools-f8a-emr-deployment-build-master/)

Emr deployment service performs two job:
 - Run the retraining job for a given ecosystem
 - Returns the precision and recall of each trained model

## Sample emr deployment request input
```
ENDPOINT: /api/v1/runjob
BODY: JSON data
{
	"bucket_name": "hpf-insights",
	"data_version":"20-12-13",
	"github_repo": "https://github.com/ravsa/test-emr",
	"ecosystem": "maven"
}
```