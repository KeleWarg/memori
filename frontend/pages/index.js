
import React, { useEffect, useState, useRef } from 'react';
import dynamic from 'next/dynamic';
import useSWR from 'swr';

const ForceGraph = dynamic(() => import('react-force-graph'), { ssr: false });

const fetcher = url => fetch(url).then(r => {
  if (!r.ok) throw new Error('Failed to fetch');
  return r.json();
});

export default function Home() {
  const [rootNodeId, setRootNodeId] = useState(null);
  
  // First, try to get conversations
  const { data: conversations } = useSWR('/api/proxy/conversations', fetcher);
  
  // Use the first conversation as root if available
  useEffect(() => {
    if (conversations && conversations.length > 0 && !rootNodeId) {
      setRootNodeId(conversations[0].id);
    }
  }, [conversations, rootNodeId]);

  const { data: graphData, error } = useSWR(
    rootNodeId ? `/api/proxy/nodes/${rootNodeId}/children?depth=2` : null,
    fetcher
  );

  const createSampleData = async () => {
    try {
      const response = await fetch('/api/proxy/seed', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const result = await response.json();
      if (result.conversation_id) {
        setRootNodeId(result.conversation_id);
      }
    } catch (err) {
      console.error('Failed to create sample data:', err);
    }
  };

  if (error) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h1>Graph Memory System</h1>
        <div style={{ color: 'red', marginBottom: '20px' }}>
          Error loading graph: {error.message}
        </div>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  if (!conversations) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h1>Graph Memory System</h1>
        <div>Loading conversations...</div>
      </div>
    );
  }

  if (conversations.length === 0) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h1>Graph Memory System</h1>
        <div style={{ marginBottom: '20px' }}>
          No conversations found. Create some sample data to get started.
        </div>
        <button 
          onClick={createSampleData}
          style={{ 
            padding: '10px 20px', 
            fontSize: '16px', 
            backgroundColor: '#007bff', 
            color: 'white', 
            border: 'none', 
            borderRadius: '5px',
            cursor: 'pointer'
          }}
        >
          Create Sample Data
        </button>
      </div>
    );
  }

  if (!graphData) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h1>Graph Memory System</h1>
        <div>Loading graph data...</div>
      </div>
    );
  }

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative' }}>
      <div style={{ 
        position: 'absolute', 
        top: '10px', 
        left: '10px', 
        zIndex: 1000,
        background: 'rgba(255,255,255,0.9)',
        padding: '10px',
        borderRadius: '5px'
      }}>
        <h3 style={{ margin: '0 0 10px 0' }}>Graph Memory System</h3>
        <div>Nodes: {graphData.nodes?.length || 0}</div>
        <div>Links: {graphData.links?.length || 0}</div>
        <button 
          onClick={createSampleData}
          style={{ 
            marginTop: '10px',
            padding: '5px 10px', 
            fontSize: '12px',
            backgroundColor: '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '3px',
            cursor: 'pointer'
          }}
        >
          Add More Data
        </button>
      </div>
      <ForceGraph
        graphData={graphData}
        nodeLabel="label"
        nodeColor={() => '#69b3a2'}
        linkColor={() => '#999'}
        onNodeClick={node => setRootNodeId(node.id)}
        width={window.innerWidth}
        height={window.innerHeight}
      />
    </div>
  );
}
