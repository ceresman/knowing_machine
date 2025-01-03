import { ImageViewer } from './components/ImageViewer'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-900 mb-6 text-center">
          Calculating Empires Visualization
        </h1>
        <ImageViewer />
      </div>
    </div>
  )
}

export default App
