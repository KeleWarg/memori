
import React, { useEffect, useState, useRef } from 'react';
import dynamic from 'next/dynamic';
import useSWR from 'swr';

const ForceGraph = dynamic(() => import('react-force-graph'), { ssr: false });

const fetcher = url => fetch(url).then(r => r.json());

export default function Home() {
  const [rootNodeId, setRootNodeId] = useState('root1');
  const { data, error } = useSWR(() => `/api_proxy/nodes/${rootNodeId}/children?depth=2`, fetcher);

  if (error) return <div>Error loading graph</div>;
  if (!data) return <div>Loading...</div>;

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <ForceGraph
        graphData={data}
        nodeLabel="label"
        onNodeClick={node => setRootNodeId(node.id)}
      />
    </div>
  );
}
