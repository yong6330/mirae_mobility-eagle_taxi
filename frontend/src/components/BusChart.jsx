const BUS_ROWS = [
  { name: '30번', runs: 32, minutes: 30 },
  { name: '34번', runs: 22.5, minutes: 40 },
  { name: '34-1번', runs: 33, minutes: 25 },
];

export default function BusChart() {
  return (
    <article className="bus-card">
      <div className="bus-card-head">
        <span>시내버스 현황</span>
        <strong>배차 간격과 운행 횟수</strong>
      </div>

      <div className="bus-chart">
        {BUS_ROWS.map((row) => (
          <div className="bus-row" key={row.name}>
            <strong>{row.name}</strong>
            <div className="bus-bars">
              <span style={{ '--size': `${(row.runs / 40) * 100}%` }}>
                <em>{row.runs}회</em>
              </span>
              <i style={{ '--size': `${(row.minutes / 40) * 100}%` }}>
                <em>{row.minutes}분</em>
              </i>
            </div>
          </div>
        ))}
      </div>

      <div className="bus-legend">
        <span><b /> 일 운행 횟수</span>
        <span><i /> 평균 배차 간격</span>
      </div>
      <small>*출처: 원주시 교통정보센터 시내버스 시간표</small>
    </article>
  );
}
