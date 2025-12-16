export default function SectionHeader(props: { title: string; right?: React.ReactNode }) {
  return (
    <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 12 }}>
      <h2>{props.title}</h2>
      {props.right}
    </div>
  )
}
