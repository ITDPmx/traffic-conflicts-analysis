
import { getServerAuthSession } from "~/server/auth";


const validateAccess = async (id: string): Promise<boolean> => {
  const response = await fetch(`http://localhost:3000/api/validate-access?access=${access}`);
  const session = await getServerAuthSession();

  const data = await response.json();
  return data.valid;
}