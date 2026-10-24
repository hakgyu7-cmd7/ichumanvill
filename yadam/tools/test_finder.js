// finder.html 판정 규칙 시험. 실행: node yadam/tools/test_finder.js
// find_hits.py 시험(test_find_hits.py)과 같은 예시를 쓴다.
const fs = require("fs");
const path = require("path");
const assert = require("assert");

const html = fs.readFileSync(path.join(__dirname, "finder.html"), "utf8");
const logic = html.slice(html.indexOf("// <logic>"), html.indexOf("// </logic>"));
const L = new Function(`${logic}; return { judge, pickSample, parseDuration, collect, YouTube, ApiError };`)();

const TODAY = "2026-10-22";
const ago = n => new Date(Date.UTC(2026, 9, 22) - n * 86400000).toISOString().slice(0, 10);
const video = (ch, subs, views, daysAgo = 30, extra = {}) => ({
  channel_id: ch, channel: ch, channel_url: "", subscribers: subs, video_id: `${ch}-${views}-${daysAgo}`,
  url: "", title: `${ch} ${views}`, published: ago(daysAgo), seconds: 900, views, likes: null,
  comments: null, is_live: false, ...extra,
});
const channelWith = (ch, subs, base, extra) =>
  [...Array(7)].map((_, i) => video(ch, subs, base, 20 + i * 5)).concat(extra);

const tests = {
  "기준표 계산 예시"() {
    const vs = channelWith("중형", 50000, 20000, [video("중형", 50000, 120000, 40), video("중형", 50000, 60000, 45)])
      .concat(channelWith("소형", 5000, 1500, [video("소형", 5000, 9000, 40)]));
    const ch = L.judge(vs, TODAY);
    assert.strictEqual(ch["중형"].baseline, 20000);
    const st = Object.fromEntries(vs.map(v => [`${v.channel}${v.views}`, v.status]));
    assert.strictEqual(st["중형120000"], "잘 됨");
    assert.strictEqual(st["중형20000"], "평범");
    assert.strictEqual(st["중형60000"], "보류");
    assert.strictEqual(st["소형9000"], "보류");
  },
  "제외 규칙"() {
    const vs = channelWith("A", 50000, 20000, [
      video("A", 50000, 300000, 30, { seconds: 59 }), video("A", 50000, 300000, 5),
      video("A", 50000, 300000, 120), video("A", 50000, 300000, 30, { is_live: true }),
    ]).concat([video("구간밖", 20000, 300000)]);
    L.judge(vs, TODAY);
    assert.deepStrictEqual(vs.slice(7).map(v => v.status),
      ["제외: 8분 미만", "제외: 14일 안 됨", "제외: 기간 밖", "제외: 라이브", "제외: 구간 밖"]);
  },
  "광고 의심과 작은 채널"() {
    const vs = [...Array(7)].map((_, i) => video("B", 50000, 20000, 20 + i, { likes: 400 }));
    vs.push(video("B", 50000, 200000, 40, { likes: 200 }));
    vs.push(...[...Array(3)].map((_, i) => video("C", 50000, 20000, 20 + i)));
    L.judge(vs, TODAY);
    assert.strictEqual(vs[7].status, "제외: 광고 유입 의심");
    assert.ok(vs[vs.length - 1].status.startsWith("제외: 채널 영상 3편뿐"));
  },
  "표본 고르기"() {
    let vs = [];
    ["M1", "M2", "M3", "M4"].forEach((n, i) => {
      vs = vs.concat(channelWith(n, 50000, 20000, [video(n, 50000, 120000 + i * 20000, 50), video(n, 50000, 110000, 60)]));
    });
    L.judge(vs, TODAY);
    const { sample, notes } = L.pickSample(vs);
    const mid = sample.filter(s => s.tier === "중형");
    assert.deepStrictEqual(mid.filter(s => s.role === "잘 됨").map(s => s.views), [180000, 160000, 140000]);
    const pairs = mid.filter(s => s.role.startsWith("평범"));
    assert.deepStrictEqual(pairs.map(s => s.channel), ["M4", "M3"]);
    assert.ok(pairs.every(p => Math.abs(p.age_days - 50) <= 5));
    assert.ok(notes.some(n => n.includes("소형")));
  },
  "길이 읽기"() {
    assert.strictEqual(L.parseDuration("PT1H2M3S"), 3723);
    assert.strictEqual(L.parseDuration("PT45S"), 45);
  },
};

(async () => {
  tests["영상 목록 없는 채널은 건너뜀"] = async () => {
    const yt = new L.YouTube("k", async url => {
      const p = new URL(url).pathname.split("/").pop();
      if (p === "channels") return { ok: true, json: async () => ({ items: [{ id: "UC" + "y".repeat(22),
        snippet: { title: "빈채널" }, statistics: { subscriberCount: "5000" },
        contentDetails: { relatedPlaylists: { uploads: "UUy" } } }] }) };
      return { ok: false, status: 404, statusText: "Not Found", json: async () => ({ error: { message: "playlist cannot be found" } }) };
    });
    const logs = [];
    assert.deepStrictEqual(await L.collect(yt, ["@빈채널"], TODAY, m => logs.push(m)), []);
    assert.ok(logs[0].includes("영상 목록이 없어 뺌"));
  };
  let failed = 0;
  for (const [name, fn] of Object.entries(tests)) {
    try { await fn(); console.log(`ok   ${name}`); } catch (e) { failed++; console.log(`FAIL ${name}\n${e.stack}`); }
  }
  process.exit(failed ? 1 : 0);
})();
