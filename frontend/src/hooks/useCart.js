import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import * as api from "../api";

/** The cart summary; pass a province code to include tax and shipping for it. */
export function useCart(province = null) {
  return useQuery({
    queryKey: ["cart", province],
    queryFn: () => api.getCart(province),
    placeholderData: keepPreviousData,
  });
}

export function useCartMutation(mutationFn) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn,
    onSuccess: (summary) => {
      queryClient.setQueryData(["cart", null], summary);
      queryClient.invalidateQueries({ queryKey: ["cart"], predicate: (query) => query.queryKey[1] !== null });
    },
  });
}
