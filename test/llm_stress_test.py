import requests
import time
import json
import argparse
import warnings
from statistics import mean, median
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
from requests.adapters import HTTPAdapter


class LLMTester:
    def __init__(self, config):
        self.api_url = config['api_url']
        self.api_key = config['api_key']
        self.model = config['model']
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.test_cases = self.load_test_cases(config['test_case_file'])
        self.results = []
        self.session = self._create_session()

    def _create_session(self):
        session = requests.Session()
        adapter = HTTPAdapter(pool_connections=20, pool_maxsize=100)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def load_test_cases(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f.readlines()]
        except IOError as e:
            warnings.warn(f"无法加载测试文件: {str(e)}, 使用默认测试用例")
            return [
                "解释量子力学的基本原理",
                "写一首关于秋天的五言绝句",
                "用Python实现快速排序算法",
                "用三个句子总结气候变化的影响"
            ]

    def generate_payload(self, prompt):
        return {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "stream": False
        }

    def send_request(self, prompt):
        start_time = time.time()
        try:
            response = self.session.post(
                self.api_url,
                headers=self.headers,
                json=self.generate_payload(prompt),
                timeout=10000
            )
            end_time = time.time()
            latency = end_time - start_time

            if response.status_code == 200:
                response_json = response.json()
                usage = response_json.get("usage", {})
                total_tokens = usage.get("total_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                tps = completion_tokens / latency if latency > 0 else 0

                return {
                    "success": True,
                    "latency": latency,
                    "status_code": response.status_code,
                    "total_tokens": total_tokens,
                    "completion_tokens": completion_tokens,
                    "tps": tps,
                    "response": response_json
                }
            else:
                return {
                    "success": False,
                    "latency": latency,
                    "status_code": response.status_code,
                    "total_tokens": 0,
                    "completion_tokens": 0,
                    "tps": 0
                }
        except Exception as e:
            return {
                "success": False,
                "latency": time.time() - start_time,
                "error": str(e),
                "status_code": 500,
                "total_tokens": 0,
                "completion_tokens": 0,
                "tps": 0
            }

    def run_test(self, num_requests, max_workers=5):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            total_cases = len(self.test_cases)
            futures = [
                executor.submit(self.send_request, self.test_cases[i % total_cases])
                for i in range(num_requests)
            ]

            for future in tqdm(futures, total=len(futures)):
                self.results.append(future.result())

    def generate_report(self):
        success_rates = sum(1 for r in self.results if r['success']) / len(self.results)
        latencies = [r['latency'] for r in self.results if r['success']]
        tps_list = [r['tps'] for r in self.results if r['success']]
        total_tokens_list = [r['total_tokens'] for r in self.results if r['success']]

        report = {
            "total_requests": len(self.results),
            "success_rate": f"{success_rates:.2%}",
            "average_latency": f"{mean(latencies):.2f}s" if latencies else "N/A",
            "median_latency": f"{median(latencies):.2f}s" if latencies else "N/A",
            "average_tps": f"{mean(tps_list):.2f} tokens/s" if tps_list else "N/A",
            "average_total_tokens": f"{mean(total_tokens_list):.2f}" if total_tokens_list else "N/A",
            "error_distribution": {}
        }

        for result in self.results:
            if not result['success']:
                error_key = result.get('error') or str(result['status_code'])
                report['error_distribution'][error_key] = report['error_distribution'].get(error_key, 0) + 1

        return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='LLM性能测试工具')
    parser.add_argument('--api-key', default='6fcf3eaf8297ab66c9bc76e54920c8ec', help='API访问密钥')
    parser.add_argument('--model', default='qwq-32b', help='模型名称')
    parser.add_argument('--requests', type=int, default=2, help='总请求数量')
    parser.add_argument('--test-file', default='./test.txt', help='测试用例文件路径')
    parser.add_argument('--api-url', default='http://10.1.110.2:8888/qwq/v1/chat/completions',
                        help='API端点URL')
    parser.add_argument('--max-workers', type=int, default=2, help='并发工作线程数')

    args = parser.parse_args()

    config = {
        "api_url": args.api_url,
        "api_key": args.api_key,
        "model": args.model,
        "test_case_file": args.test_file
    }

    tester = LLMTester(config)
    tester.run_test(args.requests, args.max_workers)
    report = tester.generate_report()

    print("\n测试结果摘要：")
    print(json.dumps(report, indent=2, ensure_ascii=False))

