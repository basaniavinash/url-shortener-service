import http from "k6/http";
import {check, sleep} from "k6";
import {SharedArray} from "k6/data";

const ids = new SharedArray("ids", () => 
    open("./ids.txt").trim().split("\n").filter(Boolean)
);

const BASE = __ENV.BASE || "http://localhost:8000";

export const options = {
    vus: Number(__ENV.VUS || 200),
    duration: __ENV.DURATION || "60s",
    thresholds: {
        http_req_failed: ["rate<0.01"],
        http_req_duration: ["p(95)<100", "p(99)<200"],
    },
}

export default function() {
    const idx = (__VU + __ITER) % ids.length
    const id = ids[idx];
    const res = http.get(`${BASE}/${id}`, {redirects: 0, tags: {endpoint: 'redirect'}});
    check(res, {"3xx": (r) => r.status >= 300 && r.status < 400});
    sleep(Math.random() * 0.05);
}