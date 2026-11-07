/**
 * Utilitário de formatação de moeda em TypeScript já existente
 */
export function formatCurrencyBRL(amount: number): string {
    return `R$ ${amount.toFixed(2)}`;
}

export function slugifyText(text: string): string {
    return text.toLowerCase().trim().replace(/[^a-z0-9]+/g, '-');
}
