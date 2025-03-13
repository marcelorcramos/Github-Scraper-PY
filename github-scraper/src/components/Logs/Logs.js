import { FadeLoader } from "react-spinners";

const Logs = ({ logs, isLoading }) => {
  if (logs === null && !isLoading) {
    return (
      <div className="mt-8">
        <h2 className="text-2xl font-bold text-center mb-4">Results:</h2>
        <div className="bg-[#333131] p-4 rounded-lg h-[70vh] overflow-y-auto">
          <p className="text-[#A5A5A5]">Your results will appear here.</p>
        </div>
      </div>
    );
  }

  if (typeof logs === "string") {
    return (
      <div className="mt-8">
        <h2 className="text-2xl font-bold text-center mb-4">Results:</h2>
        <div className="bg-[#333131] p-4 rounded-lg h-[70vh] overflow-y-auto">
          <p className="text-[#A5A5A5]">{logs}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mt-8">
      <h2 className="text-2xl font-bold text-center mb-4">Results:</h2>
      <div className="bg-[#333131] p-4 rounded-lg h-[70vh] overflow-y-auto">
        {isLoading ? (
          <div className="flex justify-center items-center h-full">
            <FadeLoader size={50} color={"#A5A5A5"} loading={true} />
          </div>
        ) : logs.length === 0 ? (
          <p className="text-[#A5A5A5]">No repositories found with the given criteria.</p>
        ) : (
          logs.map((repo, index) => (
            <div
              key={index}
              className="bg-[#444] p-4 rounded-lg mb-4 text-[#A5A5A5]"
            >
              <h3 className="text-xl font-semibold text-white">{repo.name}</h3>
              <p className="text-sm mt-2">
                <span className="font-medium">Owner:</span> {repo.owner}
              </p>
              <p className="text-sm mt-1">
                <span className="font-medium">Description:</span> {repo.description}
              </p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                <div>
                  <span className="font-medium">Stars:</span> {repo.stars}
                </div>
                <div>
                  <span className="font-medium">Forks:</span> {repo.forks}
                </div>
                <div>
                  <span className="font-medium">Created:</span>{" "}
                  {new Date(repo.created_at).toLocaleDateString()}
                </div>
                <div>
                  <span className="font-medium">Last Commit:</span>{" "}
                  {new Date(repo.last_commit).toLocaleDateString()}
                </div>
              </div>
              <a
                href={repo.link}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block mt-4 px-4 py-2 bg-[#555] text-white rounded-lg hover:bg-[#666] transition-colors"
              >
                View on GitHub
              </a>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Logs;