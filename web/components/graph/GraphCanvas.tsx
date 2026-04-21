'use client'

import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, Stars, Environment, Float, Text, Line } from '@react-three/drei'
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing'
import { useRef, useState } from 'react'
import * as THREE from 'three'
import type { GraphNode, GraphEdge } from '@/lib/types'
import { useGraphStore, dataToNodes, dataToEdges } from '@/lib/store'

function ProjectNode({ node, onClick, onHover }: { node: GraphNode; onClick: () => void; onHover: (hovering: boolean) => void }) {
  const meshRef = useRef<THREE.Mesh>(null)
  const [hovered, setHovered] = useState(false)

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.005
      meshRef.current.rotation.x += 0.002
      const scale = 1 + Math.sin(state.clock.elapsedTime * 2) * 0.05
      meshRef.current.scale.setScalar(hovered ? scale * 1.2 : scale)
    }
  })

  return (
    <Float speed={1.5} rotationIntensity={0.2} floatIntensity={0.3}>
      <mesh
        ref={meshRef}
        position={node.position}
        onClick={onClick}
        onPointerEnter={() => { setHovered(true); onHover(true) }}
        onPointerLeave={() => { setHovered(false); onHover(false) }}
      >
        <icosahedronGeometry args={[node.size, 1]} />
        <meshStandardMaterial
          color={hovered ? '#ffffff' : node.color}
          emissive={node.color}
          emissiveIntensity={hovered ? 0.8 : 0.4}
          roughness={0.3}
          metalness={0.7}
          wireframe={hovered}
        />
      </mesh>
      {(hovered || true) && (
        <Text
          position={[node.position[0], node.position[1] + node.size + 0.5, node.position[2]]}
          fontSize={0.4}
          color="#00e5ff"
          anchorX="center"
          anchorY="bottom"
          font="/fonts/Syne-Bold.ttf"
        >
          {node.label}
        </Text>
      )}
    </Float>
  )
}

function TaskNode({ node, onClick, onHover }: { node: GraphNode; onClick: () => void; onHover: (hovering: boolean) => void }) {
  const meshRef = useRef<THREE.Mesh>(null)
  const [hovered, setHovered] = useState(false)

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.01
      meshRef.current.rotation.z += 0.005
    }
  })

  return (
    <mesh
      ref={meshRef}
      position={node.position}
      onClick={onClick}
      onPointerEnter={() => { setHovered(true); onHover(true) }}
      onPointerLeave={() => { setHovered(false); onHover(false) }}
    >
      <octahedronGeometry args={[node.size, 0]} />
      <meshStandardMaterial
        color={hovered ? '#ffffff' : node.color}
        emissive={node.color}
        emissiveIntensity={hovered ? 0.6 : 0.3}
        roughness={0.4}
        metalness={0.6}
      />
    </mesh>
  )
}

function TimelineNode({ node, onHover }: { node: GraphNode; onHover: (hovering: boolean) => void }) {
  const meshRef = useRef<THREE.Mesh>(null)
  const [hovered, setHovered] = useState(false)

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.position.y = node.position[1] + Math.sin(state.clock.elapsedTime + node.position[0]) * 0.1
    }
  })

  return (
    <mesh
      ref={meshRef}
      position={node.position}
      onPointerEnter={() => { setHovered(true); onHover(true) }}
      onPointerLeave={() => { setHovered(false); onHover(false) }}
    >
      <sphereGeometry args={[node.size, 8, 8]} />
      <meshStandardMaterial
        color={hovered ? '#ffffff' : node.color}
        emissive={node.color}
        emissiveIntensity={hovered ? 0.5 : 0.2}
        transparent
        opacity={0.7}
      />
    </mesh>
  )
}

function GraphLines({ edges, nodes }: { edges: GraphEdge[]; nodes: GraphNode[] }) {
  const nodeMap = new Map(nodes.map(n => [n.id, n]))

  return (
    <group>
      {edges.map((edge, i) => {
        const source = nodeMap.get(edge.source)
        const target = nodeMap.get(edge.target)
        if (!source || !target) return null

        const points: [number, number, number][] = [
          source.position,
          target.position
        ]

        return (
          <Line
            key={i}
            points={points}
            color="#00e5ff"
            opacity={0.2}
            transparent
            lineWidth={1}
          />
        )
      })}
    </group>
  )
}

function MoodGlow({ avgMood }: { avgMood: number }) {
  const meshRef = useRef<THREE.Mesh>(null)

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.scale.setScalar(3 + Math.sin(state.clock.elapsedTime) * 0.2)
    }
  })

  const color = avgMood > 3 ? '#44ff88' : avgMood > 2 ? '#ffb800' : '#ff4444'

  return (
    <mesh ref={meshRef} position={[0, 6, 0]}>
      <sphereGeometry args={[1, 16, 16]} />
      <meshBasicMaterial
        color={color}
        transparent
        opacity={0.1}
        side={THREE.BackSide}
      />
    </mesh>
  )
}

function Scene() {
  const { data, selectNode, hoverNode, hoveredNode } = useGraphStore()

  if (!data) return null

  const nodes = dataToNodes(data)
  const edges = dataToEdges(data)

  return (
    <>
      <ambientLight intensity={0.3} />
      <pointLight position={[10, 10, 10]} intensity={1} color="#00e5ff" />
      <pointLight position={[-10, -10, -10]} intensity={0.5} color="#ffb800" />

      <Stars radius={100} depth={50} count={3000} factor={4} saturation={0} fade speed={1} />

      <MoodGlow avgMood={data.stats.avgMood7Days} />

      <GraphLines edges={edges} nodes={nodes} />

      {nodes.filter(n => n.type === 'project').map(node => (
        <ProjectNode
          key={node.id}
          node={node}
          onClick={() => selectNode(hoveredNode?.id === node.id ? null : node)}
          onHover={(h) => h ? hoverNode(node) : hoverNode(null)}
        />
      ))}

      {nodes.filter(n => n.type === 'task').map(node => (
        <TaskNode
          key={node.id}
          node={node}
          onClick={() => selectNode(node)}
          onHover={(h) => h ? hoverNode(node) : hoverNode(null)}
        />
      ))}

      {nodes.filter(n => n.type === 'timeline').map(node => (
        <TimelineNode
          key={node.id}
          node={node}
          onHover={(h) => h ? hoverNode(node) : hoverNode(null)}
        />
      ))}

      <OrbitControls
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        minDistance={5}
        maxDistance={30}
        autoRotate={false}
        makeDefault
      />

      <EffectComposer>
        <Bloom
          luminanceThreshold={0.2}
          luminanceSmoothing={0.9}
          intensity={0.8}
          radius={0.8}
        />
        <Vignette eskil={false} offset={0.1} darkness={0.8} />
      </EffectComposer>
    </>
  )
}

export default function GraphCanvas() {
  return (
    <div style={{ width: '100%', height: '100vh', background: '#0a0a0f' }}>
      <Canvas
        camera={{ position: [0, 5, 15], fov: 60 }}
        gl={{ antialias: true, alpha: false }}
        style={{ background: 'linear-gradient(180deg, #0a0a0f 0%, #12121a 100%)' }}
      >
        <Scene />
      </Canvas>
    </div>
  )
}
