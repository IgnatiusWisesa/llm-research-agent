// src/components/Result.jsx
export default function Result({ result }) {
  if (!result) return null;

  if (result.status === "complete") {
    return (
      <div>
        <h2>Answer</h2>
        <p>{result.answer}</p>
        <h3>Citations:</h3>
        <ul style={{ listStyleType: 'none', paddingLeft: 0 }}>
          {result.citations.map((c) => (
            <li key={c.id}>
              <a href={c.url} target="_blank" rel="noreferrer">
                [{c.id}] {c.title}
              </a>
            </li>
          ))}
        </ul>
      </div>
    );
  }

  if (result.status === "need_more_info") {
    return (
      <div>
        <h2>Not enough information</h2>
        <p>Try asking a more specific or related question:</p>
        <ul style={{ listStyleType: 'none', paddingLeft: 0 }}>
          {result.new_queries.map((q, idx) => (
            <li key={idx}>{q}</li>
          ))}
        </ul>
      </div>
    );
  }

  return null;
}
