import VisualizationViewer from './components/VisualizationViewer'

function App() {
  return (
    <div className="min-h-screen bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-white mb-6 text-center">
          Calculating Empires Visualization
        </h1>
        <div className="w-full h-[calc(100vh-12rem)]">
          <VisualizationViewer
            imagePath="/images/merged_visualization.png"
            initialWidth={1976}
            initialHeight={2114}
          />
        </div>
      </div>
    </div>
  )
}

export default App
