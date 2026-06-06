const BUS_ROUTES = [
  { label: '30번', runs: 32, minutes: 30 },
  { label: '34번', runs: 22.5, minutes: 40 },
  { label: '34-1번', runs: 33, minutes: 25 },
];

export default function BusChart() {
  return (
    <article className="bus-card">
      <div className="bus-card-head">
        <span>시내버스 현황</span>
        <strong>핵심 노선은 있지만 기다림이 길다.</strong>
      </div>
      <p className="bus-card-copy">
        평균 배차 간격은 1일 30회, 31분이고 이 마저 각 버스의 노선 방향이 달라
        학생들이 많이 가는 원주역, 무실동, 버스터미널은 기다림이 길다.
      </p>

      <div className="bus-chart">
        {BUS_ROUTES.map((row) => (
          <div className="bus-row route" key={row.label}>
            <strong>{row.label}</strong>
            <div className="bus-bars">
              <div className="bus-bar-line runs" style={{ '--size': `${(row.runs / 40) * 100}%` }}>
                <span />
                <em>{row.runs}</em>
              </div>
              <div className="bus-bar-line minutes" style={{ '--size': `${(row.minutes / 45) * 100}%` }}>
                <span />
                <em>{row.minutes}</em>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="bus-legend">
        <span><i className="runs" /> 배차 횟수(회)</span>
        <span><i className="minutes" /> 배차 간격(분)</span>
      </div>

      <small>*출처: 원주시 교통정보센터 시내버스 시간표</small>
    </article>
  );
}
