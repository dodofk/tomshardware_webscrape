import scrapy
import json


class Lambda_Spider(scrapy.Spider):
    name = "lambda"

    def __init__(self, split="traning", *args, **kwargs):
        super(Lambda_Spider, self).__init__(*args, **kwargs)

        assert split in ["traning", "inference"], "method must be either traning or inference"
        self.split = split

    def start_requests(self):

        if self.split == "traning":
            years = [2022, 2023]
            metrics = ["throughput", "bs"]
            precisions = [16, 32]

            for year in years:
                for metric in metrics:
                    for precision in precisions:
                        yield scrapy.Request(
                            url=f"https://21998649.fs1.hubspotusercontent-na1.net/hubfs/21998649/raw_assets/public/"
                                f"LambdaLabs/static/js/benchmarks/pytorch_{year}-train-{metric}-fp{precision}.json",
                            callback=self.parse_training,
                            cb_kwargs={"year": year, "metric": metric, "precision": precision},
                        )
        elif self.split == "inference":
            methods = [
                "Pytorch",
                "TorchScript",
                "ONNX",
                "TF",
                "TFGraphDef",
            ]

            for method in methods:
                yield scrapy.Request(
                    url=f"https://21998649.fs1.hubspotusercontent-na1.net/hubfs/21998649/raw_assets/public/"
                        f"LambdaLabs/static/js/benchmarks/yolov5-inference-latency-{method}.json",
                    callback=self.parse_inference,
                    cb_kwargs={"method": method},
                )


    def parse_training(self, response, year, metric, precision):
        data = json.loads(response.body)
        for item in data:
            item["year"] = year
            item["metric"] = metric
            item["precision"] = precision
            yield item

    def parse_inference(self, response, method):
        data = json.loads(response.body)
        for item in data:
            item["method"] = method
            yield item
