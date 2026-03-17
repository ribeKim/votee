import { useQuery } from "@tanstack/react-query";

import { fetchCurrentUser } from "../api/client";

export function useSession() {
  return useQuery({
    queryKey: ["session"],
    queryFn: fetchCurrentUser,
    retry: false
  });
}

