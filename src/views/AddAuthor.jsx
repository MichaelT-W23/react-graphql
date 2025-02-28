import { useState } from "react";
import { gql, useMutation } from "@apollo/client";

const CREATE_AUTHOR = gql`
  mutation createAuthor($name: String!, $age: Int!, $nationality: String!) {
    createAuthor(name: $name, age: $age, nationality: $nationality) {
      id
      name
      age
      nationality
    }
  }
`;

export default function AddAuthor() {
  const [name, setName] = useState("");
  const [age, setAge] = useState("");
  const [nationality, setNationality] = useState("");
  const [error, setError] = useState(null);

  const [createAuthor] = useMutation(CREATE_AUTHOR, {
    onError: (err) => setError(err.message),
  });

  const ageError = age !== "" && (age < 10 || age > 110) ? "Age must be between 10 and 110." : "";

  const isValid = name.trim() && age !== "" && age >= 10 && age <= 110 && nationality.trim();

  const submitAuthor = async (e) => {
    e.preventDefault();
    if (!isValid) return;

    try {
      await createAuthor({
        variables: { name, age: parseInt(age), nationality: nationality.trim() },
      });
      alert("Author added successfully!");
      setName("");
      setAge("");
      setNationality("");
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="flex flex-col items-center p-6">
      <h1 className="text-2xl font-bold mb-4">🖋️ Add a New Author</h1>
      <span className="block w-96 h-1 bg-teal-400 mx-auto rounded-md mb-6"></span>
      <form onSubmit={submitAuthor} className="flex flex-col gap-4 w-80">
        <label className="text-lg">
          Name:
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            type="text"
            required
            className="w-full p-2 border rounded border-gray-400"
          />
        </label>

        <label className="text-lg">
          Age:
          <input
            value={age}
            onChange={(e) => setAge(e.target.value)}
            type="number"
            required
            className="w-full p-2 border rounded border-gray-400"
          />
        </label>
        {ageError && <p className="text-red-500 text-sm">{ageError}</p>}

        <label className="text-lg">
          Nationality:
          <input
            value={nationality}
            onChange={(e) => setNationality(e.target.value)}
            type="text"
            required
            className="w-full p-2 border rounded border-gray-400"
          />
        </label>

        {error && <p className="text-red-500 text-sm">Error: {error}</p>}

        <button
          type="submit"
          disabled={!isValid}
          className={`p-2 text-white rounded ${isValid ? "bg-red-500 hover:bg-red-600" : "bg-gray-400 cursor-not-allowed"}`}
        >
          Add Author
        </button>
      </form>
    </div>
  );
}