import React from 'react'

export default function App() {
  return (
    <div style={{ fontFamily: 'sans-serif', padding: 20, maxWidth: 1200, margin: '0 auto' }}>
      <h1>Gesture User Scoring System</h1>
      
      <div style={{ 
        background: '#f5f5f5', 
        padding: 20, 
        borderRadius: 8, 
        marginBottom: 30,
        border: '1px solid #ddd'
      }}>
        <h2 style={{ marginTop: 0 }}>System Overview</h2>
        <p>
          This system <strong>observes and tracks user behavior</strong> by analyzing interaction events 
          including page views, pricing page visits, demo requests, signups, and calendar bookings.
        </p>
        <p>
          For each user, the system outputs a <strong>numerical intent or qualification score</strong> (1-100) 
          based on the captured data. This score indicates user engagement level and helps identify 
          high-intent users who are most likely to convert.
        </p>
      </div>

      <div style={{ 
        background: '#e8f4f8', 
        padding: 20, 
        borderRadius: 8, 
        marginBottom: 30,
        border: '1px solid #b3d9e6'
      }}>
        <h2 style={{ marginTop: 0 }}>How It Works</h2>
        <ol>
          <li><strong>Data Collection:</strong> User interaction events are captured and stored</li>
          <li><strong>Feature Engineering:</strong> Raw events are transformed into meaningful user features</li>
          <li><strong>Scoring:</strong> Each user receives a numerical score based on their behavior patterns</li>
          <li><strong>Ranking:</strong> Users are ranked by their intent scores for prioritization</li>
          <li><strong>Explanation:</strong> Each score includes a clear explanation of contributing factors</li>
        </ol>
      </div>

      <div style={{ 
        background: '#fff3cd', 
        padding: 15, 
        borderRadius: 8,
        border: '1px solid #ffc107'
      }}>
        <p style={{ margin: 0 }}>
          <strong>Note:</strong> To view actual user scores, ensure you've run the pipeline 
          (<code>py main.py --mode pipeline</code>) and that the data files are available.
        </p>
      </div>
    </div>
  )
}
