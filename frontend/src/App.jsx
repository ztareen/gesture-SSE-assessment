import React, { useState, useEffect } from 'react'

export default function App() {
  const [summaryStats, setSummaryStats] = useState({
    totalUsers: null,
    meanScore: null,
    medianScore: null,
    highIntent: null,
    mediumIntent: null,
    lowIntent: null
  })
  const [topUsers, setTopUsers] = useState([])
  const [scoreDistribution, setScoreDistribution] = useState(null)
  const [selectedUser, setSelectedUser] = useState(null)
  const [userFeatureContributions, setUserFeatureContributions] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Fetch data from API
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        
        // Determine API base URL
        const apiBase = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
          ? `http://${window.location.hostname}:8000`
          : ''
        
        // Fetch summary
        const summaryRes = await fetch(`${apiBase}/api/summary`)
        if (summaryRes.ok) {
          const summary = await summaryRes.json()
          if (!summary.error) {
            setSummaryStats(summary)
          }
        }
        
        // Fetch top users
        const topUsersRes = await fetch(`${apiBase}/api/top-users`)
        if (topUsersRes.ok) {
          const topUsersData = await topUsersRes.json()
          if (!topUsersData.error) {
            setTopUsers(topUsersData)
          }
        }
        
        // Fetch distribution
        const distRes = await fetch(`${apiBase}/api/distribution`)
        if (distRes.ok) {
          const dist = await distRes.json()
          if (!dist.error) {
            setScoreDistribution(dist)
          }
        }
        
        setError(null)
      } catch (err) {
        console.error('Error fetching data:', err)
        setError('Failed to load data. Make sure the pipeline has been run and the server is running.')
      } finally {
        setLoading(false)
      }
    }
    
    fetchData()
    
    // Refresh data every 5 seconds
    const interval = setInterval(fetchData, 5000)
    return () => clearInterval(interval)
  }, [])

  // Handle user selection
  const handleUserClick = (user) => {
    setSelectedUser(user)
    // Parse feature contributions if available
    if (user.feature_contributions) {
      try {
        const contributions = typeof user.feature_contributions === 'string'
          ? JSON.parse(user.feature_contributions)
          : user.feature_contributions
        setUserFeatureContributions(contributions)
      } catch (e) {
        setUserFeatureContributions(null)
      }
    } else {
      setUserFeatureContributions(null)
    }
  }

  if (loading && topUsers.length === 0) {
    return (
      <div style={{ fontFamily: 'sans-serif', padding: 20, maxWidth: 1400, margin: '0 auto', textAlign: 'center' }}>
        <h1>Gesture User Scoring System</h1>
        <p>Loading data...</p>
      </div>
    )
  }

  return (
    <div style={{ fontFamily: 'sans-serif', padding: 20, maxWidth: 1400, margin: '0 auto' }}>
      <h1>Gesture User Scoring System</h1>
      {error && (
        <div style={{ 
          background: '#f8d7da', 
          padding: 15, 
          borderRadius: 8,
          border: '1px solid #f5c6cb',
          color: '#721c24',
          marginBottom: 20
        }}>
          {error}
        </div>
      )}
      
      {/* Summary Statistics Section */}
      <div style={{ 
        background: '#f5f5f5', 
        padding: 20, 
        borderRadius: 8, 
        marginBottom: 30,
        border: '1px solid #ddd'
      }}>
        <h2 style={{ marginTop: 0 }}>Summary Statistics</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 15 }}>
          <div style={{ background: 'white', padding: 15, borderRadius: 6 }}>
            <div style={{ fontSize: 12, color: '#666', marginBottom: 5 }}>Total Users</div>
            <div style={{ fontSize: 24, fontWeight: 'bold' }}>
              {summaryStats.totalUsers !== null ? summaryStats.totalUsers : '--'}
            </div>
          </div>
          <div style={{ background: 'white', padding: 15, borderRadius: 6 }}>
            <div style={{ fontSize: 12, color: '#666', marginBottom: 5 }}>Mean Score</div>
            <div style={{ fontSize: 24, fontWeight: 'bold' }}>
              {summaryStats.meanScore !== null ? summaryStats.meanScore.toFixed(2) : '--'}
            </div>
          </div>
          <div style={{ background: 'white', padding: 15, borderRadius: 6 }}>
            <div style={{ fontSize: 12, color: '#666', marginBottom: 5 }}>Median Score</div>
            <div style={{ fontSize: 24, fontWeight: 'bold' }}>
              {summaryStats.medianScore !== null ? summaryStats.medianScore.toFixed(2) : '--'}
            </div>
          </div>
          <div style={{ background: '#d4edda', padding: 15, borderRadius: 6 }}>
            <div style={{ fontSize: 12, color: '#666', marginBottom: 5 }}>High Intent</div>
            <div style={{ fontSize: 24, fontWeight: 'bold', color: '#155724' }}>
              {summaryStats.highIntent !== null ? summaryStats.highIntent : '--'}
            </div>
          </div>
          <div style={{ background: '#fff3cd', padding: 15, borderRadius: 6 }}>
            <div style={{ fontSize: 12, color: '#666', marginBottom: 5 }}>Medium Intent</div>
            <div style={{ fontSize: 24, fontWeight: 'bold', color: '#856404' }}>
              {summaryStats.mediumIntent !== null ? summaryStats.mediumIntent : '--'}
            </div>
          </div>
          <div style={{ background: '#f8d7da', padding: 15, borderRadius: 6 }}>
            <div style={{ fontSize: 12, color: '#666', marginBottom: 5 }}>Low Intent</div>
            <div style={{ fontSize: 24, fontWeight: 'bold', color: '#721c24' }}>
              {summaryStats.lowIntent !== null ? summaryStats.lowIntent : '--'}
            </div>
          </div>
        </div>
      </div>

      {/* Score Distribution Placeholder */}
      <div style={{ 
        background: '#e8f4f8', 
        padding: 20, 
        borderRadius: 8, 
        marginBottom: 30,
        border: '1px solid #b3d9e6'
      }}>
        <h2 style={{ marginTop: 0 }}>Score Distribution</h2>
        <div style={{ 
          background: 'white', 
          padding: 40, 
          borderRadius: 6, 
          textAlign: 'center',
          minHeight: 200,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#999'
        }}>
          {scoreDistribution ? (
            <div style={{ display: 'flex', alignItems: 'flex-end', gap: 10, height: 200, padding: 20 }}>
              {scoreDistribution.ranges.map((range, idx) => {
                const maxCount = Math.max(...scoreDistribution.counts)
                const height = maxCount > 0 ? (scoreDistribution.counts[idx] / maxCount) * 150 : 0
                return (
                  <div key={range} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <div style={{
                      width: '100%',
                      background: '#4a90e2',
                      height: `${height}px`,
                      minHeight: scoreDistribution.counts[idx] > 0 ? '10px' : '0',
                      borderRadius: '4px 4px 0 0',
                      display: 'flex',
                      alignItems: 'flex-end',
                      justifyContent: 'center',
                      color: 'white',
                      fontWeight: 'bold',
                      padding: '5px 0'
                    }}>
                      {scoreDistribution.counts[idx] > 0 && scoreDistribution.counts[idx]}
                    </div>
                    <div style={{ marginTop: 10, fontSize: 12, fontWeight: 'bold' }}>{range}</div>
                  </div>
                )
              })}
            </div>
          ) : (
            <div>No distribution data available</div>
          )}
        </div>
      </div>

      {/* Top Users Table */}
      <div style={{ 
        background: '#ffffff', 
        padding: 20, 
        borderRadius: 8, 
        marginBottom: 30,
        border: '1px solid #ddd',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <h2 style={{ marginTop: 0 }}>Top Users by Intent Score</h2>
        {topUsers.length > 0 ? (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#f8f9fa', borderBottom: '2px solid #dee2e6' }}>
                <th style={{ padding: 12, textAlign: 'left' }}>Rank</th>
                <th style={{ padding: 12, textAlign: 'left' }}>Username</th>
                <th style={{ padding: 12, textAlign: 'left' }}>Location</th>
                <th style={{ padding: 12, textAlign: 'center' }}>Score</th>
                <th style={{ padding: 12, textAlign: 'center' }}>Label</th>
                <th style={{ padding: 12, textAlign: 'left' }}>Key Metrics</th>
              </tr>
            </thead>
            <tbody>
              {topUsers.map((user, idx) => (
                <tr 
                  key={user.user_id} 
                  style={{ 
                    borderBottom: '1px solid #dee2e6',
                    cursor: 'pointer',
                    background: selectedUser?.user_id === user.user_id ? '#e8f4f8' : 'transparent'
                  }}
                  onClick={() => handleUserClick(user)}
                  onMouseEnter={(e) => e.currentTarget.style.background = '#f0f0f0'}
                  onMouseLeave={(e) => e.currentTarget.style.background = selectedUser?.user_id === user.user_id ? '#e8f4f8' : 'transparent'}
                >
                  <td style={{ padding: 12 }}>{idx + 1}</td>
                  <td style={{ padding: 12, fontWeight: '500' }}>{user.username}</td>
                  <td style={{ padding: 12 }}>{user.location_city || '--'}</td>
                  <td style={{ padding: 12, textAlign: 'center', fontWeight: 'bold' }}>{user.score.toFixed(2)}</td>
                  <td style={{ padding: 12, textAlign: 'center' }}>
                    <span style={{
                      padding: '4px 8px',
                      borderRadius: 4,
                      fontSize: 12,
                      fontWeight: 'bold',
                      background: user.score_label === 'high' ? '#d4edda' : 
                                  user.score_label === 'medium' ? '#fff3cd' : '#f8d7da',
                      color: user.score_label === 'high' ? '#155724' : 
                             user.score_label === 'medium' ? '#856404' : '#721c24'
                    }}>
                      {user.score_label.toUpperCase()}
                    </span>
                  </td>
                  <td style={{ padding: 12, fontSize: 12, color: '#666' }}>
                    Signups: {user.signups || 0} | 
                    Bookings: {user.calendar_bookings || 0} | 
                    Demos: {user.demo_request_clicks || 0}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div style={{ 
            padding: 40, 
            textAlign: 'center', 
            color: '#999',
            background: '#f8f9fa',
            borderRadius: 6
          }}>
            Top users table placeholder - Load user data to display rankings
            <div style={{ marginTop: 10, fontSize: 14 }}>
              Expected data structure: Array of objects with user_id, username, score, score_label, location_city, signups, calendar_bookings, demo_request_clicks
            </div>
          </div>
        )}
      </div>

      {/* User Details & Explanation Section */}
      <div style={{ 
        background: '#ffffff', 
        padding: 20, 
        borderRadius: 8, 
        marginBottom: 30,
        border: '1px solid #ddd',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <h2 style={{ marginTop: 0 }}>User Score Explanation</h2>
        {selectedUser ? (
          <div>
            <div style={{ marginBottom: 20 }}>
              <h3>{selectedUser.username} (Score: {selectedUser.score.toFixed(2)})</h3>
              <p style={{ background: '#f8f9fa', padding: 15, borderRadius: 6 }}>
                <strong>Explanation:</strong> {selectedUser.explanation}
              </p>
            </div>
            
            {userFeatureContributions && (
              <div>
                <h4>Feature Contributions</h4>
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
                  gap: 10 
                }}>
                  {Object.entries(userFeatureContributions).map(([feature, value]) => (
                    <div key={feature} style={{ 
                      background: '#e8f4f8', 
                      padding: 10, 
                      borderRadius: 4,
                      fontSize: 14
                    }}>
                      <strong>{feature}:</strong> {typeof value === 'number' ? value.toFixed(2) : value}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div style={{ 
            padding: 40, 
            textAlign: 'center', 
            color: '#999',
            background: '#f8f9fa',
            borderRadius: 6
          }}>
            User details placeholder - Select a user to view detailed score explanation
            <div style={{ marginTop: 10, fontSize: 14 }}>
              Expected data: User object with username, score, explanation, and feature_contributions (JSON object)
            </div>
          </div>
        )}
      </div>

      {/* System Info */}
      <div style={{ 
        background: '#d1ecf1', 
        padding: 15, 
        borderRadius: 8,
        border: '1px solid #bee5eb',
        fontSize: 14
      }}>
        <p style={{ margin: 0 }}>
          <strong>Info:</strong> Data refreshes automatically every 5 seconds. Click on a user in the table above to see detailed score explanation.
        </p>
      </div>
    </div>
  )
}
