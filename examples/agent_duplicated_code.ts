/**
 * Código TypeScript gerado por um agente duplicando utilitários existentes
 */
export const formatCurrency = (amount: number): string => {
    return `R$ ${amount.toFixed(2)}`;
};

export function slugify(text: string): string {
    return text.toLowerCase().trim().replace(/[^a-z0-9]+/g, '-');
}
