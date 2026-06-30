import React, { useState, useEffect } from 'react';
import { get, BASE } from '../utils/apiClient';
import { renderTemplate } from '../utils/clientTemplate';
import { parseDeepLink } from '../utils/urlState';

/**
 * Report viewer.
 *
 * Renders a generated CSV report inline and shows a templated title bar. The
 * title supports the same {{ var }} / {% expr %} dialect as the rest of the app
 * so operators can include the report name, row count, and generated date in a
 * single line. A deep-link `banner` parameter can carry a one-off notice (e.g.
 * "shared by Alex") that is shown above the report.
 */
function ReportViewer() {
  const [dataset, setDataset] = useState('projects');
  const [rows, setRows] = useState([]);
  const [titleHtml, setTitleHtml] = useState('');
  const deepLink = parseDeepLink();

  useEffect(() => {
    fetch(`${BASE}/reports/preview?dataset=${encodeURIComponent(dataset)}`)
      .then((res) => res.text())
      .then((csv) => {
        const parsed = csv.trim().split('\n').map((line) => line.split(','));
        setRows(parsed);
        const context = { dataset, rows: parsed.length - 1, name: dataset };
        setTitleHtml(renderTemplate('Report: {{ name }} — {% rows %} rows', context));
      })
      .catch(() => {});
  }, [dataset]);

  return (
    <div className="report-viewer">
      <section className="page-hero">
        <div className="container">
          <div className="badge">Reports</div>
          <h1
            className="section-title"
            dangerouslySetInnerHTML={{ __html: titleHtml }}
          />
        </div>
      </section>

      {deepLink.banner && (
        <div
          className="report-banner"
          dangerouslySetInnerHTML={{ __html: deepLink.banner }}
        />
      )}

      <section className="section">
        <div className="container">
          <div className="report-controls">
            {['projects', 'testimonials', 'contacts', 'invoices'].map((d) => (
              <button
                key={d}
                className={`btn btn-sm ${d === dataset ? 'active' : ''}`}
                onClick={() => setDataset(d)}
              >
                {d}
              </button>
            ))}
          </div>

          <table className="report-table">
            <tbody>
              {rows.map((cells, i) => (
                <tr key={i}>
                  {cells.map((c, j) => <td key={j}>{c}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

export default ReportViewer;
