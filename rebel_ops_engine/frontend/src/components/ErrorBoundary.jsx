import React from 'react'

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error) {
    return { error }
  }

  render() {
    if (this.state.error) {
      return (
        <div className="alert alert-danger">
          <strong>Something went wrong:</strong>
          <p style={{ marginTop: 8, fontSize: 13 }}>
            {this.state.error.message || 'Unknown error'}
          </p>
          <button
            className="btn btn-outline"
            style={{ marginTop: 8 }}
            onClick={() => this.setState({ error: null })}
          >
            Retry
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
